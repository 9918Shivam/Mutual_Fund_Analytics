import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
import os
os.makedirs("reports/charts", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# ── Load Data
print("Loading data...")
nav         = pd.read_csv("data/processed/02_nav_history_clean.csv", parse_dates=["date"])
fund_master = pd.read_csv("data/processed/01_fund_master_clean.csv")
perf        = pd.read_csv("data/processed/07_scheme_performance_clean.csv")
bench       = pd.read_csv("data/processed/10_benchmark_indices_clean.csv", parse_dates=["date"])
print(f"  ✅ NAV records : {len(nav):,}")
print(f"  ✅ Funds       : {len(fund_master):,}")

# ════════════════════════════════════════════════
# TASK 1 — Daily Returns
# ════════════════════════════════════════════════
print("\n── Task 1: Computing Daily Returns...")

nav = nav.sort_values(["amfi_code","date"]).reset_index(drop=True)
nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
nav = nav.dropna(subset=["daily_return"])

# Validate distribution
print(f"  Daily return stats:")
print(f"  Mean   : {nav['daily_return'].mean()*100:.4f}%")
print(f"  Std    : {nav['daily_return'].std()*100:.4f}%")
print(f"  Min    : {nav['daily_return'].min()*100:.4f}%")
print(f"  Max    : {nav['daily_return'].max()*100:.4f}%")

# Plot distribution
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
nav["daily_return"].hist(bins=100, color="#4C72B0", edgecolor="white")
plt.title("Distribution of Daily Returns — All Funds")
plt.xlabel("Daily Return")
plt.ylabel("Frequency")
plt.axvline(0, color="red", linestyle="--", linewidth=1)

plt.subplot(1,2,2)
sample_fund = nav[nav["amfi_code"]==119551]["daily_return"]
sample_fund.hist(bins=50, color="#DD8452", edgecolor="white")
plt.title("Daily Returns — SBI Bluechip (Sample)")
plt.xlabel("Daily Return")
plt.axvline(0, color="red", linestyle="--", linewidth=1)

plt.tight_layout()
plt.savefig("reports/charts/11_daily_return_dist.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/11_daily_return_dist.png")

# ════════════════════════════════════════════════
# TASK 2 — CAGR Computation
# ════════════════════════════════════════════════
print("\n── Task 2: Computing CAGR...")

def compute_cagr(nav_df, amfi_code, years):
    fund_nav = nav_df[nav_df["amfi_code"]==amfi_code].sort_values("date")
    end_date  = fund_nav["date"].max()
    start_date = end_date - pd.DateOffset(years=years)
    start_nav = fund_nav[fund_nav["date"] >= start_date]["nav"].iloc[0]
    end_nav   = fund_nav["nav"].iloc[-1]
    cagr = (end_nav / start_nav) ** (1/years) - 1
    return round(cagr * 100, 2)

cagr_results = []
for code in fund_master["amfi_code"].unique():
    try:
        row = {
            "amfi_code" : code,
            "cagr_1yr"  : compute_cagr(nav, code, 1),
            "cagr_3yr"  : compute_cagr(nav, code, 3),
            "cagr_5yr"  : compute_cagr(nav, code, 4),  # data starts 2022
        }
        cagr_results.append(row)
    except Exception as e:
        print(f"  ⚠️  Skipping {code}: {e}")

cagr_df = pd.DataFrame(cagr_results)
cagr_df = cagr_df.merge(
    fund_master[["amfi_code","scheme_name","fund_house","category"]],
    on="amfi_code"
)
print(cagr_df[["scheme_name","cagr_1yr","cagr_3yr","cagr_5yr"]].to_string())
print(f"\n  ✅ CAGR computed for {len(cagr_df)} funds")

# ════════════════════════════════════════════════
# TASK 3 — Sharpe Ratio
# ════════════════════════════════════════════════
print("\n── Task 3: Computing Sharpe Ratio...")

RF_ANNUAL  = 0.065          # 6.5% RBI repo rate
RF_DAILY   = RF_ANNUAL / 252

def sharpe_ratio(returns):
    excess = returns - RF_DAILY
    if excess.std() == 0:
        return np.nan
    return round((excess.mean() / excess.std()) * np.sqrt(252), 4)

sharpe_df = (
    nav.groupby("amfi_code")["daily_return"]
    .apply(sharpe_ratio)
    .reset_index()
    .rename(columns={"daily_return":"sharpe_ratio"})
)
sharpe_df = sharpe_df.merge(
    fund_master[["amfi_code","scheme_name"]], on="amfi_code"
)
sharpe_df = sharpe_df.sort_values("sharpe_ratio", ascending=False)
print("  Top 5 by Sharpe Ratio:")
print(sharpe_df[["scheme_name","sharpe_ratio"]].head(5).to_string())

# ════════════════════════════════════════════════
# TASK 4 — Sortino Ratio
# ════════════════════════════════════════════════
print("\n── Task 4: Computing Sortino Ratio...")

def sortino_ratio(returns):
    excess       = returns - RF_DAILY
    downside     = returns[returns < 0]
    downside_std = downside.std()
    if downside_std == 0:
        return np.nan
    return round((excess.mean() / downside_std) * np.sqrt(252), 4)

sortino_df = (
    nav.groupby("amfi_code")["daily_return"]
    .apply(sortino_ratio)
    .reset_index()
    .rename(columns={"daily_return":"sortino_ratio"})
)
sortino_df = sortino_df.merge(
    fund_master[["amfi_code","scheme_name"]], on="amfi_code"
)
sortino_df = sortino_df.sort_values("sortino_ratio", ascending=False)
print("  Top 5 by Sortino Ratio:")
print(sortino_df[["scheme_name","sortino_ratio"]].head(5).to_string())

# ════════════════════════════════════════════════
# TASK 5 — Alpha and Beta
# ════════════════════════════════════════════════
print("\n── Task 5: Computing Alpha and Beta...")

# Prepare benchmark (Nifty 100)
nifty100 = bench[bench["index_name"]=="NIFTY100"].copy()
if len(nifty100) == 0:
    print("  ⚠️  NIFTY100 not found, using NIFTY50")
    nifty100 = bench[bench["index_name"]=="NIFTY50"].copy()

nifty100 = nifty100.sort_values("date")
nifty100["bench_return"] = nifty100["close_value"].pct_change()
nifty100 = nifty100.dropna()

alpha_beta_results = []
for code in fund_master["amfi_code"].unique():
    fund_ret = nav[nav["amfi_code"]==code][["date","daily_return"]]
    merged   = fund_ret.merge(
        nifty100[["date","bench_return"]], on="date"
    ).dropna()

    if len(merged) < 30:
        continue

    slope, intercept, r, p, se = stats.linregress(
        merged["bench_return"],
        merged["daily_return"]
    )
    alpha_beta_results.append({
        "amfi_code" : code,
        "beta"      : round(slope, 4),
        "alpha_ann" : round(intercept * 252 * 100, 4),  # annualised %
        "r_squared" : round(r**2, 4)
    })

alpha_beta_df = pd.DataFrame(alpha_beta_results)
alpha_beta_df = alpha_beta_df.merge(
    fund_master[["amfi_code","scheme_name","fund_house"]], on="amfi_code"
)
alpha_beta_df = alpha_beta_df.sort_values("alpha_ann", ascending=False)
print("  Top 5 by Alpha:")
print(alpha_beta_df[["scheme_name","alpha_ann","beta","r_squared"]].head(5).to_string())

alpha_beta_df.to_csv("data/processed/alpha_beta.csv", index=False)
print("  ✅ Saved → data/processed/alpha_beta.csv")

# ════════════════════════════════════════════════
# TASK 6 — Maximum Drawdown
# ════════════════════════════════════════════════
print("\n── Task 6: Computing Maximum Drawdown...")

def max_drawdown(nav_series):
    running_max = nav_series.cummax()
    drawdown    = nav_series / running_max - 1
    return round(drawdown.min() * 100, 2)

def max_drawdown_dates(nav_df, code):
    fund     = nav_df[nav_df["amfi_code"]==code].sort_values("date")
    run_max  = fund["nav"].cummax()
    dd       = fund["nav"] / run_max - 1
    min_idx  = dd.idxmin()
    peak_idx = fund.loc[:min_idx,"nav"].idxmax()
    return (
        fund.loc[peak_idx,"date"].strftime("%Y-%m-%d"),
        fund.loc[min_idx,"date"].strftime("%Y-%m-%d"),
        round(dd.min()*100, 2)
    )

dd_results = []
for code in fund_master["amfi_code"].unique():
    try:
        peak_dt, trough_dt, mdd = max_drawdown_dates(nav, code)
        dd_results.append({
            "amfi_code"    : code,
            "max_drawdown" : mdd,
            "peak_date"    : peak_dt,
            "trough_date"  : trough_dt
        })
    except:
        pass

dd_df = pd.DataFrame(dd_results)
dd_df = dd_df.merge(
    fund_master[["amfi_code","scheme_name"]], on="amfi_code"
)
dd_df = dd_df.sort_values("max_drawdown")
print("  Worst 5 Drawdowns:")
print(dd_df[["scheme_name","max_drawdown","peak_date","trough_date"]].head(5).to_string())

# ════════════════════════════════════════════════
# TASK 7 — Fund Scorecard
# ════════════════════════════════════════════════
print("\n── Task 7: Building Fund Scorecard...")

# Merge all metrics
scorecard = fund_master[["amfi_code","scheme_name","fund_house","category","expense_ratio_pct"]].copy()
scorecard = scorecard.merge(cagr_df[["amfi_code","cagr_3yr"]], on="amfi_code", how="left")
scorecard = scorecard.merge(sharpe_df[["amfi_code","sharpe_ratio"]], on="amfi_code", how="left")
scorecard = scorecard.merge(alpha_beta_df[["amfi_code","alpha_ann"]], on="amfi_code", how="left")
scorecard = scorecard.merge(dd_df[["amfi_code","max_drawdown"]], on="amfi_code", how="left")

# Rank each metric (higher rank = better)
n = len(scorecard)
scorecard["rank_return"]   = scorecard["cagr_3yr"].rank(ascending=True)
scorecard["rank_sharpe"]   = scorecard["sharpe_ratio"].rank(ascending=True)
scorecard["rank_alpha"]    = scorecard["alpha_ann"].rank(ascending=True)
scorecard["rank_expense"]  = scorecard["expense_ratio_pct"].rank(ascending=False)  # lower = better
scorecard["rank_drawdown"] = scorecard["max_drawdown"].rank(ascending=False)        # less negative = better

# Composite score (0-100)
scorecard["score"] = (
    0.30 * scorecard["rank_return"]  +
    0.25 * scorecard["rank_sharpe"]  +
    0.20 * scorecard["rank_alpha"]   +
    0.15 * scorecard["rank_expense"] +
    0.10 * scorecard["rank_drawdown"]
)
# Normalise to 0-100
scorecard["score"] = (
    (scorecard["score"] - scorecard["score"].min()) /
    (scorecard["score"].max() - scorecard["score"].min()) * 100
).round(2)

scorecard = scorecard.sort_values("score", ascending=False).reset_index(drop=True)
scorecard.index += 1  # rank starts at 1

print("\n  🏆 TOP 10 FUNDS BY SCORECARD:")
print(scorecard[["scheme_name","score","cagr_3yr","sharpe_ratio","alpha_ann","expense_ratio_pct","max_drawdown"]].head(10).to_string())

scorecard.to_csv("data/processed/fund_scorecard.csv")
print("\n  ✅ Saved → data/processed/fund_scorecard.csv")

# Scorecard bar chart
plt.figure(figsize=(14,8))
top15 = scorecard.head(15)
bars = plt.barh(
    top15["scheme_name"],
    top15["score"],
    color=plt.cm.RdYlGn(top15["score"]/100),
    edgecolor="black", linewidth=0.5
)
plt.xlabel("Composite Score (0–100)", fontsize=12)
plt.title("Fund Scorecard — Top 15 Funds", fontsize=15, fontweight="bold")
plt.axvline(50, color="gray", linestyle="--", alpha=0.5)
plt.gca().invert_yaxis()
for bar, score in zip(bars, top15["score"]):
    plt.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
             f"{score:.1f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig("reports/charts/12_fund_scorecard.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/12_fund_scorecard.png")

# ════════════════════════════════════════════════
# TASK 8 — Benchmark Comparison
# ════════════════════════════════════════════════
print("\n── Task 8: Benchmark Comparison...")

# Top 5 funds from scorecard
top5_codes = scorecard.head(5)["amfi_code"].tolist()
top5_names = scorecard.head(5)["scheme_name"].tolist()

# 3 year window
end_date   = nav["date"].max()
start_date = end_date - pd.DateOffset(years=3)

# Benchmark data
nifty50  = bench[bench["index_name"]=="NIFTY50"].copy()
nifty50  = nifty50[nifty50["date"] >= start_date].sort_values("date")
nifty50["norm"] = nifty50["close_value"] / nifty50["close_value"].iloc[0] * 100

nifty100 = bench[bench["index_name"].isin(["NIFTY100","NIFTY BANK"])].copy()
nifty100 = nifty100[nifty100["date"] >= start_date].sort_values("date")

plt.figure(figsize=(16,8))

# Plot benchmarks
plt.plot(nifty50["date"], nifty50["norm"],
         color="black", linewidth=2.5,
         linestyle="--", label="NIFTY 50", zorder=5)

# Plot top 5 funds
colors = ["#E41A1C","#377EB8","#4DAF4A","#FF7F00","#984EA3"]
tracking_errors = []

for i, (code, name) in enumerate(zip(top5_codes, top5_names)):
    fund_nav = nav[
        (nav["amfi_code"]==code) &
        (nav["date"] >= start_date)
    ].sort_values("date")

    fund_nav["norm"] = fund_nav["nav"] / fund_nav["nav"].iloc[0] * 100

    plt.plot(
        fund_nav["date"], fund_nav["norm"],
        color=colors[i], linewidth=1.8,
        label=name.split("-")[0].strip()
    )

    # Tracking error
    merged_te = fund_nav[["date","daily_return"]].merge(
        nifty50[["date"]].assign(
            bench_ret=nifty50["close_value"].pct_change().values
        ), on="date"
    ).dropna()

    if len(merged_te) > 0:
        te = (merged_te["daily_return"] - merged_te["bench_ret"]).std() * np.sqrt(252)
        tracking_errors.append({"fund": name, "tracking_error_pct": round(te*100,2)})

plt.title("Top 5 Funds vs NIFTY 50 — 3 Year Performance (Normalised to 100)",
          fontsize=14, fontweight="bold")
plt.xlabel("Date", fontsize=12)
plt.ylabel("Normalised Value (Base=100)", fontsize=12)
plt.legend(loc="upper left", fontsize=10)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("reports/charts/13_benchmark_comparison.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/13_benchmark_comparison.png")

# Tracking errors
if tracking_errors:
    te_df = pd.DataFrame(tracking_errors)
    print("\n  Tracking Errors vs NIFTY 50:")
    print(te_df.to_string())

print("\n" + "="*55)
print("🎉 Day 4 Complete!")
print("="*55)
print("  Deliverables:")
print("  ✅ data/processed/alpha_beta.csv")
print("  ✅ data/processed/fund_scorecard.csv")
print("  ✅ reports/charts/11_daily_return_dist.png")
print("  ✅ reports/charts/12_fund_scorecard.png")
print("  ✅ reports/charts/13_benchmark_comparison.png")