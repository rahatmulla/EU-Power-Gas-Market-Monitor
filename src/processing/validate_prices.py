
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "entsoe"

for year in [2023, 2024, 2025]:
    path = DATA_DIR / f"de_lu_prices_{year}.parquet"
    df = pd.read_parquet(path).sort_index()

    print(f"\n{'=' * 45}")
    print(f"YEAR: {year}")
    print(f"{'=' * 45}")

    print("Rows:", len(df))
    print("Duplicates:", df.index.duplicated().sum())
    print("Missing price values:", df.price_eur_mwh.isna().sum())

    gaps = df.index.to_series().diff()

    print("\nIntervals:")
    print(gaps.value_counts())

    print("\nUnusual gaps:")
    if year in [2023, 2024]:
        unusual = gaps[gaps > pd.Timedelta(hours=1)]
    else:
        unusual = gaps[
            (gaps > pd.Timedelta(minutes=15))
            & (gaps < pd.Timedelta(hours=1))
        ]

    print(unusual if not unusual.empty else "None")

    print("\nFirst timestamp:", df.index.min())
    print("Last timestamp:", df.index.max())
