
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

RAW = ROOT / "data" / "raw" / "entsoe"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

all_years = []

for year in [2023, 2024, 2025]:
    path = RAW / f"de_lu_prices_{year}_repaired.parquet"
    df = pd.read_parquet(path).sort_index()

    # Each year is defined in German local market time
    start = pd.Timestamp(
        f"{year}-01-01", tz="Europe/Berlin"
    ).tz_convert("UTC")

    end = pd.Timestamp(
        f"{year + 1}-01-01", tz="Europe/Berlin"
    ).tz_convert("UTC")

    # Convert quarter-hour prices to hourly averages.
    # Existing hourly prices remain unchanged.
    hourly = df["price_eur_mwh"].resample("h").mean()

    expected_index = pd.date_range(
        start=start,
        end=end,
        freq="h",
        inclusive="left"
    )

    hourly = hourly.reindex(expected_index)

    assert len(hourly) == len(expected_index)
    assert hourly.notna().all(), f"Missing hours in {year}"

    hourly.index.name = "timestamp_utc"

    print(f"{year}: {len(hourly)} hourly observations")

    all_years.append(hourly)

combined = pd.concat(all_years).sort_index()

assert combined.index.is_unique

output = PROCESSED / "de_lu_hourly_prices_2023_2025.parquet"
combined.to_frame().to_parquet(output)

print("\nCombined dataset:")
print("Total rows:", len(combined))
print("Missing values:", combined.isna().sum())
print("Start:", combined.index.min())
print("End:", combined.index.max())
print("Saved:", output)
