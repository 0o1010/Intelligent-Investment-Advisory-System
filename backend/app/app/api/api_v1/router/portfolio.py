from fastapi import APIRouter, Query

from sqlalchemy.orm import Session
from app.core.response import resp_200
from app.db.db_session import get_db
from typing import List, Tuple, Dict, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from pandas_datareader import data as web
from scipy.optimize import minimize
from datetime import datetime

router = APIRouter()


def download_data(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    raw = yf.download(tickers, start=start, end=end, auto_adjust=False, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Adj Close"] if "Adj Close" in raw.columns.levels[0] else raw.xs("Close", level=0, axis=1)
    else:
        col = "Adj Close" if "Adj Close" in raw.columns else "Close"
        prices = raw[[col]].rename(columns={col: tickers[0]})
    return prices.ffill().bfill()


def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute arithmetic daily returns"""
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
    """Compute cumulative net value curve from daily arithmetic returns"""
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
        options={"disp": False, "maxiter": 1000}
    )

    w_opt = pd.Series(res.x, index=returns.columns)
    w_opt = w_opt[w_opt > 1e-3]
    if len(w_opt) < min_assets:
        raise ValueError(f"Optimised portfolio holds only {len(w_opt)} assets (<{min_assets}).")

    w_opt /= w_opt.sum()
    ann_ret, ann_vol, sharpe = calculate_portfolio_performance(w_opt, returns, rf_series)
    return w_opt.to_dict(), ann_ret, ann_vol, sharpe, returns


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


def efficient_frontier(returns: pd.DataFrame, target_returns: np.ndarray) -> pd.DataFrame:
    mean_r = returns.mean()
    cov_m = returns.cov() * 252
    n = len(mean_r)

    def port_vol(w):
        return np.sqrt(w.T @ cov_m @ w)

    vols = []
    for tgt in target_returns:
        cons = (
            {"type": "eq", "fun": lambda w: w.sum() - 1},
            {"type": "eq", "fun": lambda w: w.dot(mean_r) * 252 - tgt}
        )
        bnds = tuple((0, 1) for _ in range(n))
        x0 = np.repeat(1 / n, n)
        res = minimize(port_vol, x0, method="SLSQP", bounds=bnds, constraints=cons)
        vols.append(np.nan if not res.success else res.fun)

    return pd.DataFrame({"Return": target_returns, "Volatility": vols})


def rolling_backtest(
        tickers: List[str],
        start_date: str,
        end_date: str,
        rebalance_freq: str = "BM",
        lookback_days: int = 252,
        benchmark: str = "SPY",
        rf_series: Optional[pd.Series] = None,
        **opt_kwargs
) -> Tuple[pd.Series, pd.Series]:
    prices = download_data(tickers + [benchmark], start_date, end_date)
    rets = compute_daily_returns(prices)

    rebal_dates = pd.date_range(start=rets.index[0],
                                end=rets.index[-1],
                                freq=rebalance_freq).unique()

    all_port_ret = []
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
        w_ser = _weight_series(w_opt, tickers)
        seg_ret = rets.loc[prev_date:curr_date, tickers].dot(w_ser)
        all_port_ret.append(seg_ret.iloc[1:])

    port_ret = pd.concat(all_port_ret).sort_index()
    port_cum = (1 + port_ret).cumprod()
    bench_cum = (1 + rets[benchmark]).cumprod()
    return port_cum, bench_cum


def _annual_stats(daily_ret: pd.Series, rf_series: Optional[pd.Series] = None) -> Tuple[float, float, float]:
    ann_ret = daily_ret.mean() * 252
    ann_vol = daily_ret.std() * np.sqrt(252)
    if rf_series is not None:
        rf = rf_series.reindex(daily_ret.index).ffill().bfill() / 252
        sharpe = (daily_ret - rf).mean() / daily_ret.std() * np.sqrt(252)
    else:
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
    return ann_ret, ann_vol, sharpe


@router.get("/compute")
async def get_portfolio(etf_list: str, rolling: bool = False, start_date: str = '2018-01-01',
                        end_date: Optional[str] = Query(None)):
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    etf_list = etf_list.split(",")
    rf_series = get_risk_free_rate_series(start_date, end_date)

    if rolling:
        port_cum, bench_cum = rolling_backtest(
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
        port_cum.index = port_cum.index.strftime("%Y-%m-%d")
        bench_cum.index = bench_cum.index.strftime("%Y-%m-%d")

        result = {
            "cum_curve": port_cum.to_dict(),
            "bench_cum": bench_cum.to_dict(),
            "weights": {},
            "correlation": None,
            "metrics": None
        }
    else:
        weights, ann_ret, ann_vol, sharpe, returns = optimize_custom_portfolio(
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

        w_series = _weight_series(weights, returns.columns)
        port_ret = returns.dot(w_series)
        cum_curve = compute_cumulative_returns(port_ret)
        metrics = evaluate_portfolio(weights, returns, rf_series)

        cum_curve.index = cum_curve.index.strftime("%Y-%m-%d")
        bench_prices = download_data(["SPY", "TLT"], start_date, end_date)
        bench_returns = compute_daily_returns(bench_prices)
        bench_6040 = bench_returns["SPY"] * 0.6 + bench_returns["TLT"] * 0.4
        bench_6040_cum = (1 + bench_6040).cumprod()

        ticker_name_map = {
            "AOA": "iShares Core 80/20 Aggressive Allocation ETF (AOA)",
            "AOR": "iShares Core 60/40 Balanced Allocation ETF (AOR)",
            "AOM": "iShares Core 40/60 Moderate Allocation ETF (AOM)",
            "AOK": "iShares Core 30/70 Conservative Allocation ETF (AOK)",
        }
        compare_tickers = ["AOA", "AOR", "AOM", "AOK"]
        compare_prices = download_data(compare_tickers, start_date, end_date)
        compare_returns = compute_daily_returns(compare_prices)
        compare_cum = (1 + compare_returns).cumprod()

        bench_prices_full = download_data(["SPY"], start_date, end_date)
        bench_rets_full = compute_daily_returns(bench_prices_full)
        bench_cum = (1 + bench_rets_full["SPY"]).cumprod()

        compare_cum_renamed = compare_cum.rename(columns=ticker_name_map)
        bench_cum_named = bench_cum.rename("Benchmark (SPY)")
        bench_6040_cum_named = bench_6040_cum.rename("60/40 Benchmark")
        cum_curve_named = cum_curve.rename("Buy & Hold Portfolio")
        for df in [cum_curve_named, bench_cum_named, bench_6040_cum_named, compare_cum_renamed]:
            df.index = pd.to_datetime(df.index).strftime("%Y-%m-%d")
        result = {"weights": weights,
                  "cum_curve": {},
                  "correlation": returns.corr().to_dict(),
                  "metrics": metrics}
        result['cum_curve']["Buy & Hold Portfolio"] = cum_curve_named.to_dict()
        result['cum_curve']["Benchmark (SPY)"] = bench_cum_named.to_dict()
        result['cum_curve']["60/40 Benchmark"] = bench_6040_cum_named.to_dict()
        for i in compare_cum_renamed.columns:
            result['cum_curve'][i] = compare_cum_renamed[i].to_dict()
    return resp_200(data=result)
