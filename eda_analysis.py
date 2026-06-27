import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import warnings
warnings.filterwarnings("ignore")

# ── Output folder for PNG exports
os.makedirs("reports/charts", exist_ok=True)

# ── Load all cleaned data
print("Loading data...")
nav         = pd.read_csv("data/processed/02_nav_history_clean.csv", parse_dates=["date"])
fund_master = pd.read_csv("data/processed/01_fund_master_clean.csv")
aum         = pd.read_csv("data/processed/03_aum_by_fund_house_clean.csv", parse_dates=["date"])
sip         = pd.read_csv("data/processed/04_monthly_sip_inflows_clean.csv")
cat_inflow  = pd.read_csv("data/processed/05_category_inflows_clean.csv")
folio       = pd.read_csv("data/processed/06_industry_folio_count_clean.csv")
perf        = pd.read_csv("data/processed/07_scheme_performance_clean.csv")
txn         = pd.read_csv("data/processed/08_investor_transactions_clean.csv", parse_dates=["transaction_date"])
holdings    = pd.read_csv("data/processed/09_portfolio_holdings_clean.csv")
bench       = pd.read_csv("data/processed/10_benchmark_indices_clean.csv", parse_dates=["date"])
print("✅ All data loaded!\n")

# ════════════════════════════════════════════════
# TASK 1 — NAV Trend Analysis (Plotly)
# ════════════════════════════════════════════════
print("Chart 1: NAV Trend Analysis...")

nav_merged = nav.merge(fund_master[["amfi_code","scheme_name","fund_house"]], on="amfi_code")

fig1 = px.line(
    nav_merged,
    x="date", y="nav",
    color="scheme_name",
    title="Daily NAV Trends — All 40 Schemes (2022–2026)",
    labels={"nav": "NAV (₹)", "date": "Date", "scheme_name": "Scheme"},
    template="plotly_white"
)
# Highlight 2023 bull run
fig1.add_vrect(
    x0="2023-01-01", x1="2023-12-31",
    fillcolor="green", opacity=0.08,
    annotation_text="2023 Bull Run",
    annotation_position="top left"
)
# Highlight 2024 correction
fig1.add_vrect(
    x0="2024-06-01", x1="2024-10-31",
    fillcolor="red", opacity=0.08,
    annotation_text="2024 Correction",
    annotation_position="top left"
)
fig1.update_layout(height=600, showlegend=True)
fig1.write_html("reports/charts/01_nav_trends.html")
fig1.write_image("reports/charts/01_nav_trends.png", width=1400, height=600)
print("  ✅ Saved → reports/charts/01_nav_trends.png")

# ════════════════════════════════════════════════
# TASK 2 — AUM Growth Bar Chart (Seaborn)
# ════════════════════════════════════════════════
print("Chart 2: AUM Growth by Fund House...")

aum["year"] = aum["date"].dt.year
aum_yearly = aum.groupby(["fund_house","year"])["aum_crore"].sum().reset_index()

plt.figure(figsize=(16, 7))
ax = sns.barplot(
    data=aum_yearly,
    x="fund_house", y="aum_crore",
    hue="year", palette="Blues"
)
plt.title("AUM Growth by Fund House (2022–2025)", fontsize=16, fontweight="bold")
plt.xlabel("Fund House", fontsize=12)
plt.ylabel("AUM (₹ Crore)", fontsize=12)
plt.xticks(rotation=30, ha="right")
plt.legend(title="Year")
# Highlight SBI bar
for bar in ax.patches:
    if bar.get_height() > 500000:
        bar.set_edgecolor("gold")
        bar.set_linewidth(2.5)
plt.tight_layout()
plt.savefig("reports/charts/02_aum_growth.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/02_aum_growth.png")

# ════════════════════════════════════════════════
# TASK 3 — SIP Inflow Time-Series (Plotly)
# ════════════════════════════════════════════════
print("Chart 3: SIP Inflow Trend...")

sip["month"] = pd.to_datetime(sip["month"])
sip["month_str"] = sip["month"].dt.strftime("%Y-%m")
max_sip = sip.loc[sip["sip_inflow_crore"].idxmax()]

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=sip["month_str"], y=sip["sip_inflow_crore"],
    mode="lines+markers",
    line=dict(color="#1f77b4", width=2),
    name="SIP Inflow"
))
# Annotate all-time high
fig3.add_annotation(
    x=max_sip["month_str"],
    y=max_sip["sip_inflow_crore"],
    text=f"All-Time High<br>₹{max_sip['sip_inflow_crore']:,} Cr",
    showarrow=True,
    arrowhead=2,
    bgcolor="red",
    font=dict(color="white", size=11),
    arrowcolor="red"
)
fig3.update_layout(
    title="Monthly SIP Inflows (Jan 2022 – Dec 2025)",
    xaxis_title="Month",
    yaxis_title="SIP Inflow (₹ Crore)",
    template="plotly_white",
    height=450
)
fig3.write_html("reports/charts/03_sip_trend.html")
fig3.write_image("reports/charts/03_sip_trend.png", width=1200, height=450)
print("  ✅ Saved → reports/charts/03_sip_trend.png")

# ════════════════════════════════════════════════
# TASK 4 — Category Inflow Heatmap (Seaborn)
# ════════════════════════════════════════════════
print("Chart 4: Category Inflow Heatmap...")

cat_inflow["month"] = pd.to_datetime(cat_inflow["month"])
cat_inflow["month_str"] = cat_inflow["month"].dt.strftime("%Y-%m")
pivot = cat_inflow.pivot_table(
    index="category",
    columns="month_str",
    values="net_inflow_crore",
    aggfunc="sum"
)
plt.figure(figsize=(20, 6))
sns.heatmap(
    pivot,
    cmap="YlOrRd",
    linewidths=0.3,
    annot=False,
    fmt=".0f",
    cbar_kws={"label": "Net Inflow (₹ Crore)"}
)
plt.title("Category-wise Net Inflows Heatmap (Month × Category)", fontsize=15, fontweight="bold")
plt.xlabel("Month", fontsize=11)
plt.ylabel("Fund Category", fontsize=11)
plt.xticks(rotation=45, ha="right", fontsize=7)
plt.tight_layout()
plt.savefig("reports/charts/04_category_heatmap.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/04_category_heatmap.png")

# ════════════════════════════════════════════════
# TASK 5 — Investor Demographics
# ════════════════════════════════════════════════
print("Chart 5: Investor Demographics...")

fig5, axes = plt.subplots(1, 3, figsize=(18, 6))
fig5.suptitle("Investor Demographics Analysis", fontsize=16, fontweight="bold")

# Pie — age group distribution
age_counts = txn["age_group"].value_counts()
axes[0].pie(
    age_counts.values,
    labels=age_counts.index,
    autopct="%1.1f%%",
    colors=sns.color_palette("pastel"),
    startangle=140
)
axes[0].set_title("Age Group Distribution")

# Box plot — SIP amount by age group
sip_txn = txn[txn["transaction_type"] == "SIP"]
sns.boxplot(
    data=sip_txn,
    x="age_group", y="amount_inr",
    palette="Set2", ax=axes[1]
)
axes[1].set_title("SIP Amount by Age Group")
axes[1].set_xlabel("Age Group")
axes[1].set_ylabel("Amount (₹)")
axes[1].tick_params(axis="x", rotation=30)

# Bar — gender split
gender_amt = txn.groupby("gender")["amount_inr"].sum()
axes[2].bar(
    gender_amt.index,
    gender_amt.values,
    color=["#4C72B0","#DD8452"],
    edgecolor="black"
)
axes[2].set_title("Total Investment by Gender")
axes[2].set_xlabel("Gender")
axes[2].set_ylabel("Total Amount (₹)")

plt.tight_layout()
plt.savefig("reports/charts/05_investor_demographics.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/05_investor_demographics.png")

# ════════════════════════════════════════════════
# TASK 6 — Geographic Distribution
# ════════════════════════════════════════════════
print("Chart 6: Geographic Distribution...")

fig6, axes = plt.subplots(1, 2, figsize=(18, 7))
fig6.suptitle("Geographic Distribution of Investments", fontsize=16, fontweight="bold")

# Horizontal bar — by state
state_amt = txn.groupby("state")["amount_inr"].sum().sort_values(ascending=True)
axes[0].barh(state_amt.index, state_amt.values, color="#4C72B0")
axes[0].set_title("Total SIP Amount by State")
axes[0].set_xlabel("Total Amount (₹)")

# Pie — T30 vs B30
tier_counts = txn["city_tier"].value_counts()
axes[1].pie(
    tier_counts.values,
    labels=tier_counts.index,
    autopct="%1.1f%%",
    colors=["#2196F3","#FF9800","#4CAF50"],
    startangle=90
)
axes[1].set_title("T30 vs B30 City Tier Split")

plt.tight_layout()
plt.savefig("reports/charts/06_geographic_distribution.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/06_geographic_distribution.png")

# ════════════════════════════════════════════════
# TASK 7 — Folio Count Growth
# ════════════════════════════════════════════════
print("Chart 7: Folio Count Growth...")

folio["month"] = pd.to_datetime(folio["month"])
plt.figure(figsize=(14, 5))
plt.plot(
    folio["month"], folio["total_folios_crore"],
    marker="o", color="#2196F3", linewidth=2.5, markersize=5
)
# Mark milestones
milestones = folio[folio["total_folios_crore"].isin(
    [folio["total_folios_crore"].min(), folio["total_folios_crore"].max()]
)]
for _, row in milestones.iterrows():
    plt.annotate(
        f"{row['total_folios_crore']} Cr",
        xy=(row["month"], row["total_folios_crore"]),
        xytext=(10, 10), textcoords="offset points",
        fontsize=10, color="red",
        arrowprops=dict(arrowstyle="->", color="red")
    )
plt.title("Industry Folio Count Growth (2022–2025)", fontsize=15, fontweight="bold")
plt.xlabel("Month")
plt.ylabel("Total Folios (Crore)")
plt.grid(axis="y", alpha=0.4)
plt.tight_layout()
plt.savefig("reports/charts/07_folio_growth.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/07_folio_growth.png")

# ════════════════════════════════════════════════
# TASK 8 — NAV Return Correlation Matrix
# ════════════════════════════════════════════════
print("Chart 8: NAV Return Correlation Matrix...")

# Pick 10 funds
top10_codes = fund_master["amfi_code"].head(10).tolist()
nav10 = nav[nav["amfi_code"].isin(top10_codes)].copy()
nav10 = nav10.merge(fund_master[["amfi_code","scheme_name"]], on="amfi_code")

# Pivot to wide format
nav_pivot = nav10.pivot_table(index="date", columns="scheme_name", values="nav")

# Daily returns
returns = nav_pivot.pct_change().dropna()
corr = returns.corr()

plt.figure(figsize=(12, 9))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr,
    annot=True, fmt=".2f",
    cmap="RdYlGn",
    vmin=-1, vmax=1,
    mask=mask,
    linewidths=0.5,
    cbar_kws={"label": "Correlation"}
)
plt.title("NAV Daily Return Correlation Matrix (10 Funds)", fontsize=14, fontweight="bold")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.yticks(fontsize=8)
plt.tight_layout()
plt.savefig("reports/charts/08_correlation_matrix.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/08_correlation_matrix.png")

# ════════════════════════════════════════════════
# TASK 9 — Sector Allocation Donut
# ════════════════════════════════════════════════
print("Chart 9: Sector Allocation Donut...")

# Filter equity funds only
equity_codes = fund_master[fund_master["category"]=="Equity"]["amfi_code"].tolist()
equity_holdings = holdings[holdings["amfi_code"].isin(equity_codes)]
sector_weights = equity_holdings.groupby("sector")["weight_pct"].sum().sort_values(ascending=False)

fig9, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    sector_weights.values,
    labels=sector_weights.index,
    autopct="%1.1f%%",
    pctdistance=0.75,
    wedgeprops=dict(width=0.5),
    colors=sns.color_palette("tab20", len(sector_weights)),
    startangle=90
)
ax.set_title("Sector Allocation — Equity Funds\n(Aggregate Portfolio Holdings)", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("reports/charts/09_sector_donut.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/09_sector_donut.png")

# ════════════════════════════════════════════════
# BONUS — Benchmark vs NAV comparison
# ════════════════════════════════════════════════
print("Chart 10: Benchmark vs Fund Performance...")

nifty = bench[bench["index_name"]=="NIFTY50"].copy()
nifty["normalised"] = nifty["close_value"] / nifty["close_value"].iloc[0] * 100

# Average NAV across all funds normalised
avg_nav = nav.groupby("date")["nav"].mean().reset_index()
avg_nav["normalised"] = avg_nav["nav"] / avg_nav["nav"].iloc[0] * 100

plt.figure(figsize=(14, 5))
plt.plot(nifty["date"], nifty["normalised"], label="NIFTY 50", color="orange", linewidth=2)
plt.plot(avg_nav["date"], avg_nav["normalised"], label="Avg Fund NAV", color="blue", linewidth=2)
plt.title("NIFTY 50 vs Average Fund NAV (Normalised to 100)", fontsize=14, fontweight="bold")
plt.xlabel("Date")
plt.ylabel("Normalised Value")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("reports/charts/10_benchmark_vs_nav.png", dpi=150)
plt.close()
print("  ✅ Saved → reports/charts/10_benchmark_vs_nav.png")

print("\n🎉 All 10 charts complete! Saved → reports/charts/")
print("Now open EDA_Analysis.ipynb in Jupyter to add findings!")