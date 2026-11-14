"""
to ensure that each hourly price is derived from either:
- One original hourly observation.
- Four complete 15-minute observations.
An hour with only two or three quarter-hourly observations should not silently become a valid hourly average.

"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "entsoe"
PROCESSED = ROOT / "data" / "processed"

for year in [2023, 2024, 2025]:
    df = pd.read_parquet(
        RAW / f"de_lu_prices_{year}_repaired.parquet"
    )

    counts = df["price_eur_mwh"].resample("h").count()

    invalid = counts[~counts.isin([1, 4])]

    print(f"\n{year}")
    print("Hourly observation counts:")
    print(counts.value_counts().sort_index())

    print("Incomplete hours:", len(invalid))

    if not invalid.empty:
        print(invalid.head(10))

    assert invalid.empty, f"Incomplete hours detected in {year}"

combined = pd.read_parquet(
    PROCESSED / "de_lu_hourly_prices_2023_2025.parquet"
)

assert len(combined) == 26304
assert combined.index.is_unique
assert combined.index.is_monotonic_increasing
assert combined["price_eur_mwh"].notna().all()

print("\nFINAL VALIDATION PASSED")
print("Total hourly records:", len(combined))
