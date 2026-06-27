import pandas as pd
from sqlalchemy import create_engine, text
import os

engine = create_engine("sqlite:///data/bluestock_mf.db")

def load_table(filepath, table_name):
    if not os.path.exists(filepath):
        print(f"  ⚠️  Skipping {table_name} — file not found")
        return
    df = pd.read_csv(filepath)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
    print(f"  ✅ {table_name:25s} → {count:6} rows loaded (source: {len(df)})")

def main():
    print("=" * 55)
    print("Loading cleaned CSVs into SQLite — bluestock_mf.db")
    print("=" * 55)

    tables = {
        "dim_fund":         "data/processed/01_fund_master_clean.csv",
        "fact_nav":         "data/processed/02_nav_history_clean.csv",
        "fact_aum":         "data/processed/03_aum_by_fund_house_clean.csv",
        "fact_transactions":"data/processed/08_investor_transactions_clean.csv",
        "fact_performance": "data/processed/07_scheme_performance_clean.csv",
    }

    for table, path in tables.items():
        load_table(path, table)

    print("\n🎉 Database ready → data/bluestock_mf.db")

if __name__ == "__main__":
    main()