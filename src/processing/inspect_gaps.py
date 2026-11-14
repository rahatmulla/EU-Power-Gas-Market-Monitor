
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "entsoe"

for year in [2023, 2024, 2025]:
    df = pd.read_parquet(
        DATA_DIR / f"de_lu_prices_{year}.parquet"
    )

    start = pd.Timestamp(
        f"{year}-12-30 20:00", tz="UTC"
    )
    end = pd.Timestamp(
        f"{year}-12-31 03:00", tz="UTC"
    )

    print(f"\n========== {year} ==========")
    print(df.loc[start:end].to_string())
