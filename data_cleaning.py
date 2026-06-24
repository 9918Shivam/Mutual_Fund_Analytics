import pandas as pd
import numpy as np
import os

os.makedirs("data/processed", exist_ok=True)

# ─────────────────────────────────────────
# TASK 1 — Clean nav_history.csv
# ─────────────────────────────────────────
def clean_nav_history():
    print("\n── Cleaning nav_history.csv ──")
    df = pd.read_csv("data/raw/nav_history.csv")
    print(f"  Original shape: {df.shape}")

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # Sort by fund code and date
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Forward fill missing NAV (holidays/weekends)
    df["nav_value"] = df.groupby("amfi_code")["nav_value"].ffill()

    # Remove duplicates
    df = df.drop_duplicates(subset=["amfi_code", "date"])

    # Validate NAV > 0
    invalid = df[df["nav_value"] <= 0]
    if len(invalid) > 0:
        print(f"  ⚠️  Found {len(invalid)} rows with NAV <= 0 — removing")
    df = df[df["nav_value"] > 0]

    df.to_csv("data/processed/nav_history_clean.csv", index=False)
    print(f"  ✅ Cleaned shape: {df.shape}")
    print(f"  Saved → data/processed/nav_history_clean.csv")
    return df


# ─────────────────────────────────────────
# TASK 2 — Clean investor_transactions.csv
# ─────────────────────────────────────────
def clean_transactions():
    print("\n── Cleaning investor_transactions.csv ──")
    df = pd.read_csv("data/raw/investor_transactions.csv")
    print(f"  Original shape: {df.shape}")

    # Standardise transaction_type
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    valid_types = ["Sip", "Lumpsum", "Redemption"]
    invalid_types = df[~df["transaction_type"].isin(valid_types)]
    if len(invalid_types) > 0:
        print(f"  ⚠️  Found {len(invalid_types)} invalid transaction types")
    df = df[df["transaction_type"].isin(valid_types)]
    df["transaction_type"] = df["transaction_type"].str.upper()
    df["transaction_type"] = df["transaction_type"].replace("SIP", "SIP")

    # Fix date format
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # Validate amount > 0
    df = df[df["amount"] > 0]

    # Check KYC status
    valid_kyc = ["Verified", "Pending", "Rejected"]
    df["kyc_status"] = df["kyc_status"].str.strip().str.title()
    invalid_kyc = df[~df["kyc_status"].isin(valid_kyc)]
    if len(invalid_kyc) > 0:
        print(f"  ⚠️  Found {len(invalid_kyc)} invalid KYC values")

    # Remove duplicates
    df = df.drop_duplicates()

    df.to_csv("data/processed/investor_transactions_clean.csv", index=False)
    print(f"  ✅ Cleaned shape: {df.shape}")
    print(f"  Saved → data/processed/investor_transactions_clean.csv")
    return df


# ─────────────────────────────────────────
# TASK 3 — Clean scheme_performance.csv
# ─────────────────────────────────────────
def clean_performance():
    print("\n── Cleaning scheme_performance.csv ──")
    df = pd.read_csv("data/raw/scheme_performance.csv")
    print(f"  Original shape: {df.shape}")

    # Validate return columns are numeric
    return_cols = ["return_1yr", "return_3yr", "return_5yr"]
    for col in return_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flag anomalies (returns > 100% are suspicious)
    for col in return_cols:
        if col in df.columns:
            anomalies = df[df[col] > 100]
            if len(anomalies) > 0:
                print(f"  ⚠️  {len(anomalies)} anomalies in {col} (>100%)")
                df[f"{col}_flag"] = df[col] > 100

    # Validate expense_ratio range
    if "expense_ratio" in df.columns:
        df["expense_ratio"] = pd.to_numeric(df["expense_ratio"], errors="coerce")
        outside = df[~df["expense_ratio"].between(0.1, 2.5)]
        if len(outside) > 0:
            print(f"  ⚠️  {len(outside)} funds with expense_ratio outside 0.1–2.5%")
            df["expense_ratio_flag"] = ~df["expense_ratio"].between(0.1, 2.5)

    df = df.drop_duplicates()
    df.to_csv("data/processed/scheme_performance_clean.csv", index=False)
    print(f"  ✅ Cleaned shape: {df.shape}")
    print(f"  Saved → data/processed/scheme_performance_clean.csv")
    return df


# ─────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────
if __name__ == "__main__":
    clean_nav_history()
    clean_transactions()
    clean_performance()
    print("\n🎉 All cleaning complete!")