import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="scipy.optimize")

# ==============================
# Custom Portfolio Optimizer (robust version)
# ==============================

# ------------------------------------------------------------------
# 1. Data Download & Pre‑processing
# ------------------------------------------------------------------

def download_data(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    raw = yf.download(tickers, start=start, end=end, auto_adjust=False, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Adj Close"] if "Adj Close" in raw.columns.levels[0] else raw.xs("Close", level=0, axis=1)
    else:
        col = "Adj Close" if "Adj Close" in raw.columns else "Close"
        prices = raw[[col]].rename(columns={col: tickers[0]})
    return prices.ffill().bfill()

def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices).diff().dropna()

# ------------------------------------------------------------------
# 2. Portfolio Performance Helpers
# ------------------------------------------------------------------

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

def calculate_portfolio_performance(weights, returns, rf_daily=0.0):
    w = _weight_series(weights, returns.columns)
    port_ret = returns.dot(w)
    excess = port_ret - rf_daily
    ann_ret = port_ret.mean() * 252
    ann_vol = port_ret.std() * np.sqrt(252)
    sharpe = excess.mean() / port_ret.std() * np.sqrt(252) if ann_vol > 0 else 0.0
    return ann_ret, ann_vol, sharpe

# ------------------------------------------------------------------
# 3. Portfolio Optimiser (max Sharpe)
# ------------------------------------------------------------------

def _neg_sharpe(w, returns, rf_daily):
    return -calculate_portfolio_performance(w, returns, rf_daily)[2]

def optimize_custom_portfolio(asset_list: List[str], start_date: str, end_date: str,
                               min_weight: float = 0.0, max_weight: float = 1.0,
                               min_assets: int = 2, allow_short: bool = False,
                               risk_free_rate: float = 0.0, max_volatility: Optional[float] = None
                               ) -> Tuple[Dict[str, float], float, float, float]:
    prices = download_data(asset_list, start_date, end_date)
    returns = compute_daily_returns(prices)

    n = len(asset_list)
    b_low, b_high = (-max_weight, max_weight) if allow_short else (min_weight, max_weight)
    bounds = tuple((b_low, b_high) for _ in range(n))

    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    if max_volatility:
        cons.append({"type": "ineq", "fun": lambda w: max_volatility - returns.dot(w).std() * np.sqrt(252)})

    x0 = np.repeat(1.0 / n, n)
    rf_daily = risk_free_rate / 252

    res = minimize(
        _neg_sharpe,
        x0,
        args=(returns, rf_daily),
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
    ann_ret, ann_vol, sharpe = calculate_portfolio_performance(w_opt, returns, rf_daily)
    return w_opt.to_dict(), ann_ret, ann_vol, sharpe

# ------------------------------------------------------------------
# 4. Extended Performance Metrics
# ------------------------------------------------------------------

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

# ------------------------------------------------------------------
# 5. Efficient Frontier Utilities
# ------------------------------------------------------------------

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

# ------------------------------------------------------------------
# 6. Risk-Free Rate Visualisation
# ------------------------------------------------------------------

def visualise_risk_free_rates(risk_free_rates: pd.DataFrame):
    plt.figure(figsize=(12, 6))
    yearly_rates = risk_free_rates.groupby('Year')['Rate'].mean()
    yearly_rates.plot(kind='bar', color='skyblue')
    plt.title('年度无风险利率变化')
    plt.xlabel('年份')
    plt.ylabel('无风险利率')
    plt.grid(True, axis='y')
    for i, v in enumerate(yearly_rates):
        plt.text(i, v + 0.0005, f'{v:.2%}', ha='center')
    plt.tight_layout()

# ------------------------------------------------------------------
# 7. Visualisation Module
# ------------------------------------------------------------------

def visualise_portfolio(prices: pd.DataFrame, weights, returns: pd.DataFrame,
                        port_ret: float, port_vol: float, sharpe: float,
                        risk_free_rate: float, target_points: int = 50):
    mean_r = returns.mean()
    cov_m = returns.cov() * 252
    n = len(mean_r)

    fig, ax = plt.subplots(2, 2, figsize=(20, 12))
    t_min = min(0, mean_r.min() * 252)
    t_max = mean_r.max() * 252 * 1.2
    targets = np.linspace(t_min, t_max, target_points)
    ef_df = efficient_frontier(returns, targets)
    ax[0, 0].plot(ef_df["Volatility"], ef_df["Return"], label="Efficient Frontier", lw=2)

    single_r = mean_r * 252
    single_vol = np.sqrt(np.diag(cov_m))
    ax[0, 0].scatter(single_vol, single_r, c="red", s=60, alpha=.6, label="Assets")
    for t, x, y in zip(returns.columns, single_vol, single_r):
        ax[0, 0].annotate(t, (x, y), textcoords="offset points", xytext=(5, 5))

    ax[0, 0].scatter(port_vol, port_ret, c="green", s=180, marker="*", label="Portfolio")
    ax[0, 0].plot([0, port_vol * 1.5], [risk_free_rate, risk_free_rate + sharpe * port_vol * 1.5], "r--", label="CML")
    ax[0, 0].set_title("Efficient Frontier & Portfolio")
    ax[0, 0].set_xlabel("Annual Volatility")
    ax[0, 0].set_ylabel("Annual Return")
    ax[0, 0].legend(); ax[0, 0].grid(True)

    if isinstance(weights, dict):
        w_series = pd.Series(weights)
    else:
        w_series = pd.Series(weights, index=returns.columns)
    w_series = w_series[w_series > 0.01]
    ax[0, 1].pie(w_series.values, labels=w_series.index, autopct="%1.1f%%", startangle=90, shadow=True)
    ax[0, 1].set_title("Portfolio Weights (>1%)")

    sns.heatmap(returns.corr(), ax=ax[1, 0], annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5)
    ax[1, 0].set_title("Return Correlation Matrix")

    norm_prices = prices / prices.iloc[0]
    norm_prices.plot(ax=ax[1, 1], legend=False, alpha=.6)
    w_full = _weight_series(weights, returns.columns)
    port_cum = (1 + returns.dot(w_full)).cumprod()
    ax[1, 1].plot(port_cum.index, port_cum.values, "k--", lw=3, label="Portfolio")
    ax[1, 1].set_title("Normalised Price Series & Portfolio")
    ax[1, 1].legend()

    plt.tight_layout()

    plt.figure(figsize=(12, 6))
    w_df = w_series.sort_values(ascending=False).reset_index()
    w_df.columns = ["ETF", "Weight"]
    sns.barplot(x="ETF", y="Weight", data=w_df)
    plt.title("Asset Weight Distribution")
    plt.ylim(0, w_df["Weight"].max() * 1.1)
    for i, v in enumerate(w_df["Weight"]):
        plt.text(i, v + 0.005, f"{v:.1%}", ha="center")
    plt.tight_layout()

# ------------------------------------------------------------------
# 8. Example (visualisation)
# ------------------------------------------------------------------
ETF_LIST = [
    "SPY", "QQQ", "VTI", "TLT", "GLD", "VNQ", "VYM", "IWM", "XLF", "XLK",
    "XLE", "XLY", "XLV", "XLI", "XLB", "XLC", "EFA", "EEM"
]
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Custom Portfolio Optimizer")
    parser.add_argument("--tickers", type=str, required=False, default='SPY, EEM, QQQ, IVV, VOO, XLY',
                        help="Comma-separated list of tickers, e.g., AAPL,MSFT,SPY")
    args = parser.parse_args()

    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",")]
    else:
        tickers = ETF_LIST
    print(tickers)
    w, r, v, s = optimize_custom_portfolio(
        asset_list=tickers,
        start_date="2018-01-01",
        end_date="2023-12-31",
        min_weight=0.05,
        max_weight=0.5,
        min_assets=3,
        allow_short=False,
        risk_free_rate=0.03,
        max_volatility=0.2
    )
    prices = download_data(tickers, "2018-01-01", "2023-12-31")
    rets = compute_daily_returns(prices)
    visualise_portfolio(prices, w, rets, r, v, s, risk_free_rate=0.03)

    # --- Evaluate & print metrics ---
    rf_df = pd.DataFrame({"Rate": 0.03}, index=prices.index)  # 整个时间段都为 0.03
    metrics = evaluate_portfolio(w, rets, rf_df["Rate"])
    print("\nPortfolio Metrics")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")

    # Show plots when running as script
    plt.show()
