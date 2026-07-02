import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings("ignore")
import os
os.makedirs("reports/charts", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# ── Load Data
print("Loading data...")
nav         = pd.read_csv("data/processed/02_nav_history_clean.csv", parse_dates=["date"])
fund_master = pd.read_csv("data/processed/01_fund_master_clean.csv")
txn         = pd.read_csv("data/processed/08_investor_transactions_clean.csv", parse_dates=["transaction_date"])
holdings    = pd.read_csv("data/processed/09_portfolio_holdings_clean.csv")
scorecard   = pd.read_csv("data/processed/fund_scorecard.csv")

nav = nav.sort_values(["amfi_code","date"]).reset_index(drop=True)
nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
nav_clean = nav.dropna(subset=["daily_return"])
print(f"  ✅ Loaded {len(nav_clean):,} NAV records")

# ════════════════════════════════════════════════
# TASK 1 — Historical VaR (95%) and CVaR
# ════════════════════════════════════════════════
print("\n── Task 1: Computing VaR and CVaR...")

var_results = []
for code in fund_master["amfi_code"].unique():
    returns = nav_clean[nav_clean["amfi_code"]==code]["daily_return"]
    if len(returns) < 30:
        continue
    var_95  = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    var_results.append({
        "amfi_code"  : code,
        "var_95_pct" : round(var_95 * 100, 4),
        "cvar_95_pct": round(cvar_95 * 100, 4),
        "total_days" : len(returns)
    })

var_df = pd.DataFrame(var_results).merge(
    fund_master[["amfi_code","scheme_name","category","risk_category"]], on="amfi_code"
)
var_df = var_df.sort_values("var_95_pct")

print("  Highest Risk Funds (Worst VaR):")
print(var_df[["scheme_name","var_95_pct","cvar_95_pct"]].head(5).to_string())
print("\n  Lowest Risk Funds (Best VaR):")
print(var_df[["scheme_name","var_95_pct","cvar_95_pct"]].tail(5).to_string())

var_df.to_csv("data/processed/var_cvar_report.csv", index=False)
print("  ✅ Saved → data/processed/var_cvar_report.csv")

# Plot VaR chart
plt.figure(figsize=(14,8))
colors = ["#F44336" if v < -1.5 else "#FF9800" if v < -0.5 else "#4CAF50"
          for v in var_df["var_95_pct"]]
plt.barh(var_df["scheme_name"], var_df["var_95_pct"],
         color=colors, edgecolor="black", linewidth=0.4)
plt.axvline(-1.5, color="red",    linestyle="--", alpha=0.6, label="High Risk (-1.5%)")
plt.axvline(-0.5, color="orange", linestyle="--", alpha=0.6, label="Medium Risk (-0.5%)")
plt.xlabel("VaR 95% (%)", fontsize=12)
plt.title("Historical VaR (95%) — All 40 Funds", fontsize=14, fontweight="bold")
plt.legend()
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("reports/charts/20_var_cvar.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/20_var_cvar.png")

# ════════════════════════════════════════════════
# TASK 2 — Rolling 90-day Sharpe Ratio
# ════════════════════════════════════════════════
print("\n── Task 2: Computing Rolling Sharpe...")

RF_DAILY = 0.065 / 252

# Pick 5 key funds from scorecard
top5 = scorecard.head(5)[["amfi_code","scheme_name"]].reset_index(drop=True)

plt.figure(figsize=(16,7))
colors = ["#E41A1C","#377EB8","#4DAF4A","#FF7F00","#984EA3"]

for i, row in top5.iterrows():
    code = row["amfi_code"]
    name = row["scheme_name"]
    fund_ret = nav_clean[nav_clean["amfi_code"]==code].set_index("date")["daily_return"]

    rolling_mean = fund_ret.rolling(90).mean()
    rolling_std  = fund_ret.rolling(90).std()
    rolling_sharpe = ((rolling_mean - RF_DAILY) / rolling_std) * np.sqrt(252)
    rolling_sharpe = rolling_sharpe.dropna()

    plt.plot(
        rolling_sharpe.index,
        rolling_sharpe.values,
        color=colors[i],
        linewidth=1.5,
        label=name.split("-")[0].strip()
    )

plt.axhline(1.0,  color="green", linestyle="--", alpha=0.5, label="Good Sharpe (1.0)")
plt.axhline(0.0,  color="red",   linestyle="--", alpha=0.5, label="Zero")
plt.title("Rolling 90-Day Sharpe Ratio — Top 5 Funds", fontsize=14, fontweight="bold")
plt.xlabel("Date", fontsize=12)
plt.ylabel("Rolling Sharpe Ratio", fontsize=12)
plt.legend(loc="upper left", fontsize=9)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("reports/charts/21_rolling_sharpe.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/21_rolling_sharpe.png")

# ════════════════════════════════════════════════
# TASK 3 — Investor Cohort Analysis
# ════════════════════════════════════════════════
print("\n── Task 3: Investor Cohort Analysis...")

# Get first transaction year per investor
first_txn = txn.groupby("investor_id")["transaction_date"].min().reset_index()
first_txn["cohort_year"] = first_txn["transaction_date"].dt.year
txn_cohort = txn.merge(first_txn[["investor_id","cohort_year"]], on="investor_id")

# SIP only
sip_cohort = txn_cohort[txn_cohort["transaction_type"]=="SIP"]

cohort_summary = sip_cohort.groupby("cohort_year").agg(
    investor_count  = ("investor_id", "nunique"),
    avg_sip_amount  = ("amount_inr",  "mean"),
    total_invested  = ("amount_inr",  "sum"),
    total_sip_txns  = ("investor_id", "count")
).reset_index()
cohort_summary["avg_sip_amount"] = cohort_summary["avg_sip_amount"].round(2)
cohort_summary["total_invested"]  = cohort_summary["total_invested"].round(0)

# Top fund per cohort
top_fund_per_cohort = (
    txn_cohort.groupby(["cohort_year","amfi_code"])
    .size().reset_index(name="txn_count")
    .sort_values("txn_count", ascending=False)
    .groupby("cohort_year").first().reset_index()
    .merge(fund_master[["amfi_code","scheme_name"]], on="amfi_code")
    [["cohort_year","scheme_name"]]
    .rename(columns={"scheme_name":"top_fund"})
)
cohort_summary = cohort_summary.merge(top_fund_per_cohort, on="cohort_year")
print("  Cohort Analysis Results:")
print(cohort_summary.to_string())

# Plot cohort
fig, axes = plt.subplots(1, 2, figsize=(16,6))
axes[0].bar(
    cohort_summary["cohort_year"].astype(str),
    cohort_summary["avg_sip_amount"],
    color=["#2196F3","#4CAF50","#FF9800","#E91E63"],
    edgecolor="black"
)
axes[0].set_title("Avg SIP Amount by Cohort Year", fontweight="bold")
axes[0].set_xlabel("Cohort Year")
axes[0].set_ylabel("Avg SIP Amount (₹)")
for i, v in enumerate(cohort_summary["avg_sip_amount"]):
    axes[0].text(i, v+50, f"₹{v:,.0f}", ha="center", fontsize=9)

axes[1].bar(
    cohort_summary["cohort_year"].astype(str),
    cohort_summary["total_invested"]/1e6,
    color=["#2196F3","#4CAF50","#FF9800","#E91E63"],
    edgecolor="black"
)
axes[1].set_title("Total Invested by Cohort Year (₹ Millions)", fontweight="bold")
axes[1].set_xlabel("Cohort Year")
axes[1].set_ylabel("Total Invested (₹ Millions)")

plt.tight_layout()
plt.savefig("reports/charts/22_cohort_analysis.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/22_cohort_analysis.png")

# ════════════════════════════════════════════════
# TASK 4 — SIP Continuity Analysis
# ════════════════════════════════════════════════
print("\n── Task 4: SIP Continuity Analysis...")

sip_txn = txn[txn["transaction_type"]=="SIP"].copy()
sip_txn = sip_txn.sort_values(["investor_id","transaction_date"])

# Investors with 6+ SIP transactions
sip_counts = sip_txn.groupby("investor_id").size()
active_investors = sip_counts[sip_counts >= 6].index
sip_active = sip_txn[sip_txn["investor_id"].isin(active_investors)].copy()

# Compute gap between consecutive SIPs per investor
sip_active["prev_date"] = sip_active.groupby("investor_id")["transaction_date"].shift(1)
sip_active["gap_days"]  = (sip_active["transaction_date"] - sip_active["prev_date"]).dt.days
sip_active = sip_active.dropna(subset=["gap_days"])

investor_gaps = sip_active.groupby("investor_id").agg(
    avg_gap_days  = ("gap_days", "mean"),
    max_gap_days  = ("gap_days", "max"),
    sip_count     = ("gap_days", "count")
).reset_index()
investor_gaps["avg_gap_days"] = investor_gaps["avg_gap_days"].round(1)
investor_gaps["at_risk"]      = investor_gaps["avg_gap_days"] > 35

at_risk_count     = investor_gaps["at_risk"].sum()
total_investors   = len(investor_gaps)
continuity_rate   = ((total_investors - at_risk_count) / total_investors * 100).round(2)

print(f"  Total investors with 6+ SIPs : {total_investors:,}")
print(f"  At-risk investors (gap>35d)  : {at_risk_count:,}")
print(f"  SIP Continuity Rate          : {continuity_rate}%")

# Gap distribution plot
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.hist(
    investor_gaps["avg_gap_days"],
    bins=30, color="#2196F3",
    edgecolor="white"
)
plt.axvline(35, color="red", linestyle="--", linewidth=2, label="At-Risk Threshold (35 days)")
plt.title("Distribution of Avg SIP Gap Days", fontweight="bold")
plt.xlabel("Avg Gap Between SIPs (days)")
plt.ylabel("Number of Investors")
plt.legend()

plt.subplot(1,2,2)
labels = ["Regular\n(gap ≤ 35 days)", "At-Risk\n(gap > 35 days)"]
sizes  = [total_investors - at_risk_count, at_risk_count]
colors = ["#4CAF50","#F44336"]
plt.pie(sizes, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=90)
plt.title("SIP Continuity Status", fontweight="bold")

plt.tight_layout()
plt.savefig("reports/charts/23_sip_continuity.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/23_sip_continuity.png")

# ════════════════════════════════════════════════
# TASK 5 — Fund Recommender
# ════════════════════════════════════════════════
print("\n── Task 5: Fund Recommender...")

def recommend_funds(risk_appetite):
    risk_map = {
        "Low"      : ["Low"],
        "Moderate" : ["Moderate", "Moderately High"],
        "High"     : ["High", "Very High"]
    }
    if risk_appetite not in risk_map:
        print("  ❌ Invalid input. Choose: Low / Moderate / High")
        return

    valid_grades = risk_map[risk_appetite]
    eligible = fund_master[fund_master["risk_category"].isin(valid_grades)]
    eligible = eligible.merge(
        scorecard[["amfi_code","sharpe_ratio","cagr_3yr","score"]],
        on="amfi_code", how="left"
    )
    eligible = eligible.sort_values("sharpe_ratio", ascending=False)
    top3 = eligible.head(3)

    print(f"\n  🎯 Top 3 Recommended Funds for '{risk_appetite}' Risk Appetite:")
    print(f"  {'Fund Name':<50} {'Sharpe':>8} {'3yr CAGR':>10} {'Score':>8}")
    print(f"  {'-'*80}")
    for _, row in top3.iterrows():
        print(f"  {row['scheme_name']:<50} {row['sharpe_ratio']:>8.2f} {row['cagr_3yr']:>9.2f}% {row['score']:>8.2f}")
    return top3

recommend_funds("Low")
recommend_funds("Moderate")
recommend_funds("High")

# ════════════════════════════════════════════════
# TASK 6 — Sector HHI Concentration
# ════════════════════════════════════════════════
print("\n── Task 6: Sector HHI Concentration...")

equity_codes = fund_master[fund_master["category"]=="Equity"]["amfi_code"].tolist()
equity_holdings = holdings[holdings["amfi_code"].isin(equity_codes)].copy()

hhi_results = []
for code in equity_codes:
    fund_h = equity_holdings[equity_holdings["amfi_code"]==code]
    if len(fund_h) == 0:
        continue
    weights = fund_h["weight_pct"].values
    hhi = np.sum(weights ** 2)
    hhi_results.append({
        "amfi_code"    : code,
        "hhi"          : round(hhi, 2),
        "num_sectors"  : fund_h["sector"].nunique(),
        "top_sector"   : fund_h.groupby("sector")["weight_pct"].sum().idxmax()
    })

hhi_df = pd.DataFrame(hhi_results).merge(
    fund_master[["amfi_code","scheme_name"]], on="amfi_code"
)
hhi_df = hhi_df.sort_values("hhi", ascending=False)

print("  HHI Concentration Results:")
print(hhi_df[["scheme_name","hhi","num_sectors","top_sector"]].to_string())

# HHI Chart
plt.figure(figsize=(14,7))
colors = ["#F44336" if h > 2000 else "#FF9800" if h > 1000 else "#4CAF50"
          for h in hhi_df["hhi"]]
plt.barh(hhi_df["scheme_name"], hhi_df["hhi"],
         color=colors, edgecolor="black", linewidth=0.4)
plt.axvline(2000, color="red",    linestyle="--", alpha=0.6, label="Highly Concentrated (>2000)")
plt.axvline(1000, color="orange", linestyle="--", alpha=0.6, label="Moderately Concentrated (>1000)")
plt.xlabel("HHI Score", fontsize=12)
plt.title("Sector Concentration (HHI) — Equity Funds", fontsize=14, fontweight="bold")
plt.legend()
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("reports/charts/24_hhi_concentration.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/24_hhi_concentration.png")

print("\n" + "="*55)
print("🎉 Day 6 Analytics Complete!")
print("="*55)
print("  ✅ data/processed/var_cvar_report.csv")
print("  ✅ reports/charts/20_var_cvar.png")
print("  ✅ reports/charts/21_rolling_sharpe.png")
print("  ✅ reports/charts/22_cohort_analysis.png")
print("  ✅ reports/charts/23_sip_continuity.png")
print("  ✅ reports/charts/24_hhi_concentration.png")