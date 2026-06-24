import pandas as pd
from sqlalchemy import create_engine, text
import os

# Connect to SQLite database
engine = create_engine("sqlite:///data/bluestock_mf.db")

def load_table(df, table_name):
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    # Verify row count
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
    print(f"  ✅ {table_name}: {count} rows loaded (source: {len(df)} rows)")

def main():
    print("── Loading cleaned CSVs into SQLite ──\n")

    files = {
        "fact_nav":          "data/processed/nav_history_clean.csv",
        "fact_transactions": "data/processed/investor_transactions_clean.csv",
        "fact_performance":  "data/processed/scheme_performance_clean.csv",
    }

    for table, path in files.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            load_table(df, table)
        else:
            print(f"  ⚠️  Skipping {table} — file not found: {path}")

    print("\n🎉 Database loaded → data/bluestock_mf.db")

if __name__ == "__main__":
    main()