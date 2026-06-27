import pandas as pd
import os
import glob

# ─────────────────────────────────────────
# TASK 3 — Load all 10 CSVs
# ─────────────────────────────────────────

raw_path = "data/raw"

# Automatically pick up every CSV in data/raw
csv_files = glob.glob(f"{raw_path}/*.csv")

print("=" * 60)
print("TASK 3 — Loading all CSV files from data/raw/")
print("=" * 60)

anomalies = []

for filepath in csv_files:
    filename = os.path.basename(filepath)
    print(f"\n{'─'*50}")
    print(f"FILE: {filename}")

    try:
        df = pd.read_csv(filepath)

        print(f"  Shape     : {df.shape}")
        print(f"  Columns   : {list(df.columns)}")
        print(f"\n  Dtypes:")
        print(df.dtypes.to_string())
        print(f"\n  Head:")
        print(df.head())

        # Check anomalies
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        duplicates = df.duplicated().sum()

        if len(missing) > 0:
            note = f"{filename}: Missing values in {list(missing.index)}"
            anomalies.append(note)
            print(f"\n  ⚠️  Missing values:\n{missing}")

        if duplicates > 0:
            note = f"{filename}: {duplicates} duplicate rows found"
            anomalies.append(note)
            print(f"\n  ⚠️  Duplicate rows: {duplicates}")

    except Exception as e:
        print(f"  ❌ Error loading {filename}: {e}")

# ─────────────────────────────────────────
# TASK 6 — Explore fund_master.csv
# ─────────────────────────────────────────

print("\n")
print("=" * 60)
print("TASK 6 — Exploring 01_fund_master.csv")
print("=" * 60)

try:
    fm = pd.read_csv("data/raw/01_fund_master.csv")

    print(f"\n📌 Unique Fund Houses ({fm['fund_house'].nunique()}):")
    print(fm['fund_house'].unique())

    print(f"\n📌 Unique Categories ({fm['category'].nunique()}):")
    print(fm['category'].unique())

    print(f"\n📌 Unique Sub-Categories ({fm['sub_category'].nunique()}):")
    print(fm['sub_category'].unique())

    print(f"\n📌 Unique Risk Grades ({fm['risk_category'].nunique()}):")
    print(fm['risk_category'].unique())

    print(f"\n📌 AMFI Code Structure (sample):")
    print(fm[['amfi_code', 'scheme_name', 'fund_house']].head(10))

except Exception as e:
    print(f"❌ Error: {e}")

# ─────────────────────────────────────────
# TASK 7 — Validate AMFI Codes
# ─────────────────────────────────────────

print("\n")
print("=" * 60)
print("TASK 7 — Validating AMFI Codes")
print("=" * 60)

try:
    fm  = pd.read_csv("data/raw/01_fund_master.csv")
    nav = pd.read_csv("data/raw/02_nav_history.csv")

    fm_codes  = set(fm["amfi_code"].unique())
    nav_codes = set(nav["amfi_code"].unique())

    missing_in_nav = fm_codes - nav_codes
    extra_in_nav   = nav_codes - fm_codes

    print(f"\n  Total funds in fund_master  : {len(fm_codes)}")
    print(f"  Total funds in nav_history  : {len(nav_codes)}")

    if len(missing_in_nav) == 0:
        print("\n  ✅ All AMFI codes in fund_master exist in nav_history!")
    else:
        print(f"\n  ⚠️  {len(missing_in_nav)} codes MISSING from nav_history:")
        print(missing_in_nav)

    if len(extra_in_nav) > 0:
        print(f"\n  ⚠️  {len(extra_in_nav)} extra codes in nav_history:")
        print(extra_in_nav)

    # Data Quality Summary
    summary = f"""
DATA QUALITY SUMMARY — Day 1
==============================
Total funds in fund_master  : {len(fm_codes)}
Total funds in nav_history  : {len(nav_codes)}
Missing from nav_history    : {len(missing_in_nav)}
Extra in nav_history        : {len(extra_in_nav)}

Anomalies found across CSVs:
  - 04_monthly_sip_inflows.csv: Missing values in [yoy_growth_pct] (12 rows)
    Reason: First 12 months have no previous year to compare — expected.
"""
    print(summary)

    os.makedirs("reports", exist_ok=True)
    with open("reports/data_quality_summary.txt", "w") as f:
        f.write(summary)
    print("  ✅ Saved → reports/data_quality_summary.txt")

except Exception as e:
    print(f"❌ Error: {e}")