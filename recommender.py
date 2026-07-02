import pandas as pd

def recommend_funds(risk_appetite):
    fund_master = pd.read_csv("data/processed/01_fund_master_clean.csv")
    scorecard   = pd.read_csv("data/processed/fund_scorecard.csv")

    risk_map = {
        "Low"      : ["Low"],
        "Moderate" : ["Moderate", "Moderately High"],
        "High"     : ["High", "Very High"]
    }

    if risk_appetite not in risk_map:
        print("❌ Invalid input. Please enter: Low / Moderate / High")
        return None

    valid_grades = risk_map[risk_appetite]
    eligible = fund_master[fund_master["risk_category"].isin(valid_grades)]
    eligible = eligible.merge(
        scorecard[["amfi_code","sharpe_ratio","cagr_3yr","score","max_drawdown"]],
        on="amfi_code", how="left"
    ).dropna(subset=["sharpe_ratio"])
    eligible = eligible.sort_values("sharpe_ratio", ascending=False)
    top3 = eligible.head(3)

    print(f"\n{'='*65}")
    print(f"  🎯 Fund Recommendations — Risk Appetite: {risk_appetite}")
    print(f"{'='*65}")
    print(f"  {'Rank':<6} {'Fund Name':<45} {'Sharpe':>7} {'3yr%':>7} {'Score':>7}")
    print(f"  {'-'*65}")
    for rank, (_, row) in enumerate(top3.iterrows(), 1):
        name = row["scheme_name"][:43]
        print(f"  {rank:<6} {name:<45} {row['sharpe_ratio']:>7.2f} {row['cagr_3yr']:>6.1f}% {row['score']:>7.1f}")
    print(f"{'='*65}\n")
    return top3

if __name__ == "__main__":
    print("🏦 Bluestock Fund Recommender")
    print("Enter your risk appetite:")
    risk = input("Low / Moderate / High → ").strip().title()
    recommend_funds(risk)