
"""Validate ENTSO-E historical market forecast downloads."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "entsoe"

datasets = [
    "load_forecast",
    "wind_solar_forecast"
]

for name in datasets:
    print(f"\n========== {name} ==========")

    for year in [2023, 2024, 2025]:
        files = sorted(
            DATA_DIR.glob(f"de_lu_{name}_{year}_??.parquet")
        )

        print(f"\nYear: {year}")
        print(f"Monthly files: {len(files)}/12")

        if not files:
            print("ERROR: No files found")
            continue

        data = pd.concat(
            [pd.read_parquet(path) for path in files]
        ).sort_index()

        start = pd.Timestamp(
            f"{year}-01-01", tz="Europe/Berlin"
        ).tz_convert("UTC")

        end = pd.Timestamp(
            f"{year + 1}-01-01", tz="Europe/Berlin"
        ).tz_convert("UTC")

        expected = pd.date_range(
            start=start,
            end=end,
            freq="15min",
            inclusive="left"
        )

        missing = expected.difference(data.index)
        unexpected = data.index.difference(expected)

        print("Rows:", len(data))
        print("Expected rows:", len(expected))
        print("Duplicate timestamps:", data.index.duplicated().sum())
        print("Missing timestamps:", len(missing))
        print("Unexpected timestamps:", len(unexpected))
        print("Missing values:")
        print(data.isna().sum().to_string())

        print("Interval distribution:")
        print(
            data.index.to_series()
            .diff()
            .value_counts()
            .head()
        )

        if (
            len(files) == 12
            and len(missing) == 0
            and len(unexpected) == 0
            and data.index.is_unique
            and not data.isna().any().any()
        ):
            print("VALIDATION PASSED")
        else:
            print("VALIDATION NEEDS REVIEW")

