
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "entsoe"

recovered = {
    2023: ("2023-12-30 23:00:00", 36.54),
    2024: ("2024-12-30 23:00:00", 50.49),
    2025: ("2025-12-30 23:00:00", 94.87),
}

for year, (timestamp, price) in recovered.items():
    source = DATA_DIR / f"de_lu_prices_{year}.parquet"

    df = pd.read_parquet(source).copy()

    missing_time = pd.Timestamp(timestamp, tz="UTC")

    # Add only if the observation is absent
    if missing_time not in df.index:
        df.loc[missing_time, "price_eur_mwh"] = price

    df = df.sort_index()

    # Validate
    assert df.index.is_unique
    assert df.index.is_monotonic_increasing
    assert df["price_eur_mwh"].notna().all()

    # Preserve original raw data; save repaired version separately
    output = DATA_DIR / f"de_lu_prices_{year}_repaired.parquet"
    df.to_parquet(output)

    print(f"\n{year}")
    print(f"Rows: {len(df)}")
    print(f"Missing values: {df.price_eur_mwh.isna().sum()}")
    print("Intervals:")
    print(df.index.to_series().diff().value_counts())
    print(f"Saved: {output.name}")
