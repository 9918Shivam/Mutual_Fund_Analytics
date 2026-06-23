import pandas as pd
import os

# List your 10 CSV file names here (put CSVs inside data/raw/)
csv_files = [
    "fund_master.csv",
    "nav_history.csv",
    # add the rest here...
]

for file in csv_files:
    path = os.path.join("data", "raw", file)
    try:
        df = pd.read_csv(path)
        print(f"\n{'='*50}")
        print(f"FILE: {file}")
        print(f"Shape: {df.shape}")
        print(f"Dtypes:\n{df.dtypes}")
        print(f"Head:\n{df.head()}")
    except FileNotFoundError:
        print(f"[MISSING] {file} not found in data/raw/")