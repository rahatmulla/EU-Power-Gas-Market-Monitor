
from pathlib import Path
import os
import time

import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

api_key = os.getenv("ENTSOE_API_KEY")
if not api_key:
    raise ValueError("Missing ENTSOE_API_KEY")

client = EntsoePandasClient(api_key=api_key)

# Three complete calendar years
years = [2023, 2024, 2025]

output_dir = ROOT / "data" / "raw" / "entsoe"
output_dir.mkdir(parents=True, exist_ok=True)

for year in years:
    print(f"\nDownloading {year}...")

    start = pd.Timestamp(f"{year}-01-01", tz="Europe/Berlin")
    end = pd.Timestamp(f"{year + 1}-01-01", tz="Europe/Berlin")

    output_path = output_dir / f"de_lu_prices_{year}.parquet"

    if output_path.exists():
        print(f"Skipping {year}: file already exists")
        continue

    try:
        prices = client.query_day_ahead_prices(
            country_code="DE_LU",
            start=start,
            end=end
        )

        prices = prices.rename("price_eur_mwh").to_frame()
        prices.index = prices.index.tz_convert("UTC")
        prices.index.name = "timestamp_utc"

        # Remove any inclusive-end boundary observation
        prices = prices.loc[
            (prices.index >= start.tz_convert("UTC"))
            & (prices.index < end.tz_convert("UTC"))
        ].sort_index()

        if prices.empty:
            raise ValueError(f"No data returned for {year}")

        if not prices.index.is_unique:
            raise ValueError(f"Duplicate timestamps in {year}")

        prices.to_parquet(output_path)

        print(f"Saved: {output_path}")
        print(f"Rows: {len(prices)}")
        print(f"Missing prices: {prices.price_eur_mwh.isna().sum()}")
        print("Intervals:")
        print(prices.index.to_series().diff().value_counts().head())

        time.sleep(2)

    except Exception as exc:
        print(f"FAILED for {year}: {exc}")
