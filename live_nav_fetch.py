import requests
import pandas as pd
import os

# Fund name → AMFI scheme code
funds = {
    "HDFC_Top100":     125497,
    "SBI_Bluechip":    119551,
    "ICICI_Bluechip":  120503,
    "Nippon_LargeCap": 118632,
    "Axis_Bluechip":   119092,
    "Kotak_Bluechip":  120841,
}

os.makedirs("data/raw", exist_ok=True)

for fund_name, code in funds.items():
    url = f"https://api.mfapi.in/mf/{code}"
    print(f"Fetching {fund_name}...")

    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data["data"])
    df["fund_name"] = fund_name
    df["scheme_code"] = code

    save_path = f"data/raw/{fund_name}_nav.csv"
    df.to_csv(save_path, index=False)
    print(f"  ✅ Saved {len(df)} rows → {save_path}")

print("\n🎉 All 6 funds fetched successfully!")