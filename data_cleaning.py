import pandas as pd
import numpy as np
import os

os.makedirs("data/processed", exist_ok=True)

# ─────────────────────────────────────────
# TASK 1 — Clean 02_nav_history.csv
# ─────────────────────────────────────────
def clean_nav_history():
    print("\n── Cleaning 02_nav_history.csv ──")
    df = pd.read_csv("data/raw/02_nav_history.csv")
    print(f"  Original shape : {df.shape}")

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Sort by fund + date
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Forward fill missing NAV per fund
    df["nav"] = df.groupby("amfi_code")["nav"].ffill()

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    print(f"  Duplicates removed : {before - len(df)}")

    # Validate NAV > 0
    invalid = df[df["nav"] <= 0]
    if len(invalid) > 0:
        print(f"  ⚠️  {len(invalid)} rows with NAV <= 0 removed")
    df = df[df["nav"] > 0]

    df.to_csv("data/processed/02_nav_history_clean.csv", index=False)
    print(f"  ✅ Cleaned shape  : {df.shape}")
    print(f"  Saved → data/processed/02_nav_history_clean.csv")
    return df


# ─────────────────────────────────────────
# TASK 2 — Clean 08_investor_transactions.csv
# ─────────────────────────────────────────
def clean_transactions():
    print("\n── Cleaning 08_investor_transactions.csv ──")
    df = pd.read_csv("data/raw/08_investor_transactions.csv")
    print(f"  Original shape : {df.shape}")

    # Fix date format
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce"
    )

    # Standardise transaction_type
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    print(f"  Unique transaction types found : {df['transaction_type'].unique()}")
    valid_types = ["Sip", "Lumpsum", "Redemption"]
    invalid_types = df[~df["transaction_type"].isin(valid_types)]
    if len(invalid_types) > 0:
        print(f"  ⚠️  {len(invalid_types)} invalid transaction types removed")
    df = df[df["transaction_type"].isin(valid_types)]
    df["transaction_type"] = df["transaction_type"].str.upper()

    # Validate amount > 0
    before = len(df)
    df = df[df["amount_inr"] > 0]
    print(f"  Rows removed (amount <= 0) : {before - len(df)}")

    # Check KYC status
    valid_kyc = ["Verified", "Pending", "Rejected"]
    df["kyc_status"] = df["kyc_status"].str.strip().str.title()
    invalid_kyc = df[~df["kyc_status"].isin(valid_kyc)]
    if len(invalid_kyc) > 0:
        print(f"  ⚠️  {len(invalid_kyc)} invalid KYC values found")
    print(f"  Unique KYC values : {df['kyc_status'].unique()}")

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    print(f"  Duplicates removed : {before - len(df)}")

    df.to_csv("data/processed/08_investor_transactions_clean.csv", index=False)
    print(f"  ✅ Cleaned shape  : {df.shape}")
    print(f"  Saved → data/processed/08_investor_transactions_clean.csv")
    return df


# ─────────────────────────────────────────
# TASK 3 — Clean 07_scheme_performance.csv
# ─────────────────────────────────────────
def clean_performance():
    print("\n── Cleaning 07_scheme_performance.csv ──")
    df = pd.read_csv("data/raw/07_scheme_performance.csv")
    print(f"  Original shape : {df.shape}")

    # Validate return columns are numeric
    return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        nulls = df[col].isnull().sum()
        if nulls > 0:
            print(f"  ⚠️  {nulls} non-numeric values in {col}")

    # Flag anomalies (returns > 100% suspicious)
    for col in return_cols:
        anomalies = df[df[col] > 100]
        if len(anomalies) > 0:
            print(f"  ⚠️  {len(anomalies)} anomalies in {col} (>100%)")
            df[f"{col}_flag"] = df[col] > 100
        else:
            print(f"  ✅ {col} — no anomalies")

    # Validate expense_ratio range 0.1 to 2.5
    df["expense_ratio_pct"] = pd.to_numeric(
        df["expense_ratio_pct"], errors="coerce"
    )
    outside = df[~df["expense_ratio_pct"].between(0.1, 2.5)]
    if len(outside) > 0:
        print(f"  ⚠️  {len(outside)} funds outside expense ratio range:")
        print(outside[["scheme_name", "expense_ratio_pct"]])
        df["expense_ratio_flag"] = ~df["expense_ratio_pct"].between(0.1, 2.5)
    else:
        print(f"  ✅ All expense ratios within 0.1–2.5% range")

    # Remove duplicates
    df = df.drop_duplicates()

    df.to_csv("data/processed/07_scheme_performance_clean.csv", index=False)
    print(f"  ✅ Cleaned shape  : {df.shape}")
    print(f"  Saved → data/processed/07_scheme_performance_clean.csv")
    return df


# ─────────────────────────────────────────
# Also copy remaining CSVs to processed/
# ─────────────────────────────────────────
def copy_remaining_files():
    print("\n── Copying remaining CSVs to processed/ ──")
    remaining = [
        "01_fund_master.csv",
        "03_aum_by_fund_house.csv",
        "04_monthly_sip_inflows.csv",
        "05_category_inflows.csv",
        "06_industry_folio_count.csv",
        "09_portfolio_holdings.csv",
        "10_benchmark_indices.csv",
    ]
    for f in remaining:
        df = pd.read_csv(f"data/raw/{f}")
        df.to_csv(f"data/processed/{f.replace('.csv','_clean.csv')}", index=False)
        print(f"  ✅ Copied → data/processed/{f.replace('.csv','_clean.csv')}")


# ─────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────
if __name__ == "__main__":
    clean_nav_history()
    clean_transactions()
    clean_performance()
    copy_remaining_files()
    print("\n🎉 All cleaning complete! Check data/processed/")