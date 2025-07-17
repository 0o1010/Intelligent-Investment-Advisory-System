from fastapi import APIRouter, Query

import random
from app.core.response import resp_200
import openai
from typing import List, Tuple, Dict, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from pandas_datareader import data as web
from scipy.optimize import minimize
from datetime import datetime

router = APIRouter()
api_keys = ['f1cbcbfc-b023-4743-b959-47a625a8852f', '7bd2d286-06d5-494d-9b8a-e6492add377e',
            'd055fb6c-0c4e-4e7d-8ddb-447bdb19d6e4', 'b83ced09-7a1d-4e4d-94eb-7434d8afe798']


def download_data(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    raw = yf.download(tickers, start=start, end=end, auto_adjust=False, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Adj Close"] if "Adj Close" in raw.columns.levels[0] else raw.xs("Close", level=0, axis=1)
    else:
        col = "Adj Close" if "Adj Close" in raw.columns else "Close"
        prices = raw[[col]].rename(columns={col: tickers[0]})
    return prices.ffill().bfill()


def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()


def get_risk_free_rate_series(start: str, end: str) -> pd.Series:
    rf_df = web.DataReader("TB3MS", "fred", start, end) / 100
    rf_df = rf_df.asfreq("D", method="ffill").rename(columns={"TB3MS": "Rate"})
    return rf_df["Rate"]


def _weight_series(weights, columns):
    if isinstance(weights, dict):
        ser = pd.Series(0.0, index=columns)
        for k, v in weights.items():
            if k in ser.index:
                ser[k] = v
    elif isinstance(weights, pd.Series):
        ser = weights.reindex(columns).fillna(0.0)
    else:
        if len(weights) != len(columns):
            raise ValueError("Weights length mismatch.")
        ser = pd.Series(weights, index=columns)
    return ser.astype(float)


def calculate_portfolio_performance(weights, returns, rf_series=None):
    w = _weight_series(weights, returns.columns)
    port_ret = returns.dot(w)
    if rf_series is not None:
        aligned_rf = rf_series.reindex(port_ret.index).ffill().bfill()
        excess = port_ret - aligned_rf / 252
    else:
        excess = port_ret
    ann_ret = port_ret.mean() * 252
    ann_vol = port_ret.std() * np.sqrt(252)
    sharpe = excess.mean() / port_ret.std() * np.sqrt(252) if ann_vol > 0 else 0.0
    return ann_ret, ann_vol, sharpe


def compute_cumulative_returns(daily_returns: pd.Series) -> pd.Series:
    return (1 + daily_returns).cumprod()


def optimize_custom_portfolio(asset_list: List[str], start_date: str, end_date: str,
                              min_weight: float = 0.0, max_weight: float = 1.0,
                              min_assets: int = 2, allow_short: bool = False,
                              rf_series: Optional[pd.Series] = None,
                              max_volatility: Optional[float] = None
                              ):
    prices = download_data(asset_list, start_date, end_date)
    returns = compute_daily_returns(prices)
    n = len(asset_list)
    b_low, b_high = (-max_weight, max_weight) if allow_short else (min_weight, max_weight)
    bounds = tuple((b_low, b_high) for _ in range(n))
    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    if max_volatility:
        cons.append({"type": "ineq", "fun": lambda w: max_volatility - returns.dot(w).std() * np.sqrt(252)})
    x0 = np.repeat(1.0 / n, n)

    def _neg_sharpe(w):
        return -calculate_portfolio_performance(w, returns, rf_series)[2]

    res = minimize(
        _neg_sharpe,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=cons,
        options={"disp": False, "maxiter": 500, "ftol": 1e-6}
    )

    w_opt = pd.Series(res.x, index=returns.columns)
    w_opt = w_opt[w_opt > 1e-3]
    if len(w_opt) < min_assets:
        raise ValueError(f"Optimised portfolio holds only {len(w_opt)} assets (<{min_assets}).")
    w_opt /= w_opt.sum()
    ann_ret, ann_vol, sharpe = calculate_portfolio_performance(w_opt, returns, rf_series)
    return w_opt.to_dict(), ann_ret, ann_vol, sharpe, returns, prices


def evaluate_portfolio(weights, returns, rf_series):
    w = _weight_series(weights, returns.columns)
    port_ret = returns.dot(w)
    cum = (1 + port_ret).cumprod()
    total_ret = cum.iloc[-1] - 1
    years = (cum.index[-1] - cum.index[0]).days / 365.25
    ann_ret = (1 + total_ret) ** (1 / years) - 1
    ann_vol = port_ret.std() * np.sqrt(252)

    aligned_rf = rf_series.reindex(port_ret.index).ffill().bfill()
    excess = port_ret - aligned_rf / 252
    sharpe = excess.mean() / port_ret.std() * np.sqrt(252) if ann_vol > 0 else 0.0

    peak = cum.expanding().max()
    mdd = (cum / peak - 1).min()

    return {
        "Total Return": total_ret,
        "Annualised Return": ann_ret,
        "Annualised Vol": ann_vol,
        "Sharpe": sharpe,
        "Max Drawdown": mdd
    }


def static_backtest_with_rebalancing(
        prices: pd.DataFrame,
        weights: Dict[str, float],
        rebalance_freq: str = "BM"
) -> pd.Series:
    returns = compute_daily_returns(prices)
    rebal_dates = pd.date_range(start=returns.index[0], end=returns.index[-1], freq=rebalance_freq).unique()
    port_ret = pd.Series(dtype=float)
    for i in range(1, len(rebal_dates)):
        prev_date, curr_date = rebal_dates[i - 1], rebal_dates[i]
        seg = returns.loc[prev_date:curr_date]
        w_ser = _weight_series(weights, returns.columns)
        seg_ret = seg.dot(w_ser)
        port_ret = pd.concat([port_ret, seg_ret.iloc[1:]])
    port_ret = port_ret.sort_index()
    port_cum = (1 + port_ret).cumprod()
    return port_cum


def rolling_backtest(
        tickers: List[str],
        start_date: str,
        end_date: str,
        rebalance_freq: str = "BM",
        lookback_days: int = 120,
        benchmark: str = "SPY",
        rf_series: Optional[pd.Series] = None,
        **opt_kwargs
) -> Tuple[pd.Series, pd.Series, List[Dict[str, float]]]:
    prices = download_data(tickers + [benchmark], start_date, end_date)
    rets = compute_daily_returns(prices)
    rebal_dates = pd.date_range(start=rets.index[0], end=rets.index[-1], freq=rebalance_freq).unique()
    all_port_ret = []
    all_weights = []
    for i in range(1, len(rebal_dates)):
        prev_date, curr_date = rebal_dates[i - 1], rebal_dates[i]
        hist_start = curr_date - pd.Timedelta(days=lookback_days)
        hist_slice = rets.loc[hist_start:curr_date - pd.Timedelta(days=1), tickers]
        w_opt, *_ = optimize_custom_portfolio(
            asset_list=tickers,
            start_date=str(hist_start.date()),
            end_date=str((curr_date - pd.Timedelta(days=1)).date()),
            rf_series=rf_series,
            **opt_kwargs
        )
        all_weights.append(w_opt)
        w_ser = _weight_series(w_opt, tickers)
        seg_ret = rets.loc[prev_date:curr_date, tickers].dot(w_ser)
        all_port_ret.append(seg_ret.iloc[1:])
    port_ret = pd.concat(all_port_ret).sort_index()
    port_cum = (1 + port_ret).cumprod()
    bench_cum = (1 + rets[benchmark]).cumprod()
    return port_cum, bench_cum, all_weights


@router.get("/compute")
async def get_portfolio(etf_list: str, rolling: bool,
                        start_date: str = '2018-01-01',
                        end_date: Optional[str] = Query(None)):
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    etf_list = etf_list.split(",")
    rf_series = get_risk_free_rate_series(start_date, end_date)
    weights, ann_ret, ann_vol, sharpe, returns, prices = optimize_custom_portfolio(
        asset_list=etf_list,
        start_date=start_date,
        end_date=end_date,
        min_weight=0.05,
        max_weight=0.5,
        min_assets=3,
        allow_short=False,
        rf_series=rf_series,
        max_volatility=0.2
    )
    ticker_name_map = {
        "AOA": "iShares Core 80/20 Aggressive Allocation ETF (AOA)",
        "AOR": "iShares Core 60/40 Balanced Allocation ETF (AOR)",
        "AOM": "iShares Core 40/60 Moderate Allocation ETF (AOM)",
        "AOK": "iShares Core 30/70 Conservative Allocation ETF (AOK)",
        "Benchmark (SPY)": "BlackRock 60/40 Target Allocation (BVDAX)",
        "60/40 Benchmark": "BlackRock 60/40 Target Allocation Fund (BIGPX)"
    }
    result = {"weights": weights,
              "cum_curve": {},
              "correlation": returns.corr().to_dict(),
              "metrics": None}
    bench_6040_prices = download_data(["SPY", "TLT"], start_date, end_date)
    bench_6040_rets = compute_daily_returns(bench_6040_prices)
    bench_6040 = bench_6040_rets["SPY"] * 0.6 + bench_6040_rets["TLT"] * 0.4
    bench_6040_cum = (1 + bench_6040).cumprod().rename(ticker_name_map["60/40 Benchmark"])
    compare_tickers = ["AOA", "AOR", "AOM", "AOK"]
    compare_prices = download_data(compare_tickers, start_date, end_date)
    compare_returns = compute_daily_returns(compare_prices)
    compare_cum = (1 + compare_returns).cumprod()
    compare_cum = compare_cum.rename(columns={k: v for k, v in ticker_name_map.items() if k in compare_cum.columns})

    if rolling:
        port_cum, bench_cum, all_weights = rolling_backtest(
            tickers=etf_list,
            start_date=start_date,
            end_date=end_date,
            rf_series=rf_series,
            min_weight=0.05,
            max_weight=0.5,
            min_assets=3,
            allow_short=False,
            max_volatility=0.2
        )
        rolling_daily_ret = port_cum.pct_change().dropna()
        rolling_metrics = {
            "Total Return": port_cum.iloc[-1] - 1,
            "Annualised Return": (port_cum.iloc[-1]) ** (252 / len(port_cum)) - 1,
            "Annualised Vol": rolling_daily_ret.std() * np.sqrt(252),
            "Sharpe": (rolling_daily_ret.mean() / rolling_daily_ret.std()) * np.sqrt(252),
            "Max Drawdown": ((port_cum / port_cum.cummax()) - 1).min()
        }

        port_cum_named = port_cum.rename("Rolling Portfolio")
        bench_cum_named = bench_cum.rename(ticker_name_map["Benchmark (SPY)"])

        all_curves = pd.concat([port_cum_named, bench_cum_named, bench_6040_cum, compare_cum], axis=1)
        all_curves = all_curves.dropna(how='any')
        result['metrics'] = rolling_metrics
    else:
        rebalance_curve = static_backtest_with_rebalancing(prices, weights, rebalance_freq='BM')
        bench_prices = download_data(["SPY"], start_date, end_date)
        bench_rets = compute_daily_returns(bench_prices)
        bench_cum = (1 + bench_rets["SPY"]).cumprod().rename(ticker_name_map["Benchmark (SPY)"])

        rebalance_curve_named = rebalance_curve.rename("Static Rebalance Portfolio")
        all_curves = pd.concat([rebalance_curve_named, bench_cum, bench_6040_cum, compare_cum], axis=1)
        all_curves = all_curves.dropna(how='any')
        metrics = evaluate_portfolio(weights, returns, rf_series)
        result['metrics'] = metrics
    for i in all_curves.columns:
        all_curves[i].index = all_curves[i].index.strftime("%Y-%m-%d")
        result['cum_curve'][i] = all_curves[i].to_dict()
    output = suggest(model='Meta-Llama-3.3-70B-Instruct', port_data=result)
    result['explanation'] = output
    if rolling:
        all_curves = all_curves.rename(columns={"Rolling Portfolio": "Portfolio"})
    else:
        all_curves = all_curves.rename(columns={"Static Rebalance Portfolio": "Portfolio"})

    row_labels = [
        "Portfolio",
        "BlackRock 60/40 Target Allocation (BVDAX)",
        "BlackRock 60/40 Target Allocation Fund (BIGPX)",
        "iShares Core 80/20 Aggressive Allocation ETF (AOA)",
        "iShares Core 60/40 Balanced Allocation ETF (AOR)",
        "iShares Core 40/60 Moderate Allocation ETF (AOM)",
        "iShares Core 30/70 Conservative Allocation ETF (AOK)"
    ]
    col_labels = ["Total Return", "Annualised Return",
                  "Annualised Volatility", "Max Drawdown", "Sharpe Ratio"]

    metrics_df = pd.DataFrame(index=row_labels, columns=col_labels, dtype=float)
    for lbl in row_labels:
        if lbl == "Portfolio":
            metrics_df.loc[lbl] = [result['metrics']['Total Return'], result['metrics']['Annualised Return'],
                                   result['metrics']['Annualised Vol'], result['metrics']['Max Drawdown'],
                                   result['metrics']['Sharpe']]
        else:
            series = all_curves[lbl]
            total_ret = series.iloc[-1] / series.iloc[0] - 1
            yrs = (series.index[-1] - series.index[0]).days / 365.0
            ann_ret = (1 + total_ret) ** (1 / yrs) - 1 if yrs > 0 else np.nan
            daily_ret = series.pct_change().dropna()
            ann_vol = daily_ret.std() * np.sqrt(252)
            sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(252) if daily_ret.std() > 0 else 0.0
            mdd = ((series / series.cummax()) - 1).min()
            metrics_df.loc[lbl] = [total_ret, ann_ret, ann_vol, mdd, sharpe]

    result["metrics_table"] = metrics_df.to_dict(orient="index")

    start_str = all_curves.index[0].strftime("%Y-%m-%d")
    end_str = all_curves.index[-1].strftime("%Y-%m-%d")
    result["test_period"] = f"Test Period: {start_str} to {end_str}"
    return resp_200(data=result)


def build_explanation_messages(port_data: dict, risk_profile: str = "Balanced") -> list:
    system_prompt = (
        "You are a senior portfolio strategist at a digital wealth advisory platform. "
        "Your job is to explain investment portfolios to clients in a professional, clear, and client-friendly way. "
        "You should highlight the advantages, risks, and investment strategies of the selected ETFs, "
        "and help clients understand the design philosophy and adjustment logic of the portfolio. "
        "Do not invent data; rely only on the inputs provided."
    )

    weights_text = "\n".join([f"- {k}: {v * 100:.1f}%" for k, v in port_data['weights'].items()])
    metrics = port_data['metrics']
    context_prompt = (
        f"Client risk profile: {risk_profile}\n"
        f"Portfolio allocation:\n{weights_text}\n\n"
        "Historical metrics:\n"
        f"- Annualised return: {metrics['Annualised Return'] * 100:.2f}%\n"
        f"- Annualised volatility: {metrics['Annualised Vol'] * 100:.2f}%\n"
        f"- Sharpe ratio: {metrics['Sharpe']:.2f}\n"
        f"- Max drawdown: {metrics['Max Drawdown'] * 100:.2f}%\n"
        f"Current date: {datetime.now().date().isoformat()}"
    )

    task_prompt = (
        "Please write a concise and client-friendly explanation (around 150 words) of the following:\n\n"
        "**1. Portfolio Performance** – Summarize key performance indicators such as annualized return, annualized volatility, Sharpe ratio, and maximum drawdown.\n\n"
        "**2. Diversification Details** – Briefly explain what types of ETFs (e.g., sector-based, thematic, regional, etc.) are included, and how they contribute to overall diversification.\n\n"
        "Use clear sections with bold headers, and make the explanation easy for a non-professional client to understand.\n"
        "Finally, provide a friendly suggestion that the client can further personalize the portfolio according to their own risk tolerance, investment horizon, or specific preferences (such as focusing more on certain sectors, regions, or adding/removing certain asset types). Encourage the client to communicate their needs for a more tailored solution."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context_prompt + "\n\n" + task_prompt}
    ]


def suggest(model, port_data):
    client = openai.OpenAI(
        api_key=api_keys[random.randint(0, len(api_keys) - 1)],
        base_url="https://api.sambanova.ai/v1",
    )
    messages = build_explanation_messages(port_data)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        top_p=0.1,
        max_tokens=4096
    )
    output = response.choices[0].message.content

    return output
