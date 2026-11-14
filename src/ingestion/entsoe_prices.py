
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

# Project root
ROOT = Path(__file__).resolve().parents[2]

# Load credentials
load_dotenv(ROOT / ".env")

api_key = os.getenv("ENTSOE_API_KEY")

if not api_key:
    raise ValueError("ENTSOE_API_KEY is missing from .env")

# Initialize ENTSO-E client
client = EntsoePandasClient(api_key=api_key)

# Download one month first to validate the pipeline
start = pd.Timestamp("2025-01-01", tz="Europe/Berlin")
end = pd.Timestamp("2025-02-01", tz="Europe/Berlin")

print("Downloading Germany-Luxembourg day-ahead prices...")

prices = client.query_day_ahead_prices(
    country_code="DE_LU",
    start=start,
    end=end
)

# Standardize timestamps and values
prices = prices.rename("price_eur_mwh").to_frame()
prices.index = prices.index.tz_convert("UTC")
prices.index.name = "timestamp_utc"

prices = prices.sort_index()

# Enforce the requested interval [start, end)
start_utc = start.tz_convert("UTC")
end_utc = end.tz_convert("UTC")

prices = prices.loc[
    (prices.index >= start_utc)
    & (prices.index < end_utc)
]

# Validate timestamps
assert prices.index.is_unique, "Duplicate timestamps found"
assert prices.index.is_monotonic_increasing, "Timestamps not sorted"

print("\nData validation:")
print("Rows after filtering:", len(prices))
print("Missing values:", prices.isna().sum().sum())

print("\nTime interval distribution:")
print(prices.index.to_series().diff().value_counts())

# Save locally
output_dir = ROOT / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "de_lu_day_ahead_2025_01.parquet"
prices.to_parquet(output_path)

print("\nDownload successful!")
print(f"Rows: {len(prices)}")
print(f"Missing prices: {prices['price_eur_mwh'].isna().sum()}")
print(f"Start: {prices.index.min()}")
print(f"End: {prices.index.max()}")
print(f"Saved to: {output_path}")

print("\nFirst five records:")
print(prices.head())
