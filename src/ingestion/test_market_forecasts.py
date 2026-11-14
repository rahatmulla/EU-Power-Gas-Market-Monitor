
"""Test ENTSO-E demand, wind and solar forecast downloads."""

from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

api_key = os.getenv("ENTSOE_API_KEY")
if not api_key:
    raise ValueError("Missing ENTSOE_API_KEY")

client = EntsoePandasClient(api_key=api_key)

start = pd.Timestamp("2024-01-01", tz="Europe/Berlin")
end = pd.Timestamp("2024-01-08", tz="Europe/Berlin")

output_dir = ROOT / "data" / "raw" / "entsoe"
output_dir.mkdir(parents=True, exist_ok=True)

datasets = {
    "load_forecast": lambda: client.query_load_forecast(
        country_code="DE_LU",
        start=start,
        end=end
    ),
    "wind_solar_forecast": lambda: (
        client.query_wind_and_solar_forecast(
            country_code="DE_LU",
            start=start,
            end=end
        )
    )
}

for name, fetch in datasets.items():
    print(f"\nDownloading {name}...")

    try:
        data = fetch()

        if isinstance(data, pd.Series):
            data = data.to_frame()

        data.index = data.index.tz_convert("UTC")
        data.index.name = "timestamp_utc"

        data = data.loc[
            (data.index >= start.tz_convert("UTC"))
            & (data.index < end.tz_convert("UTC"))
        ].sort_index()

        if data.empty:
            raise ValueError("Empty dataset")

        if not data.index.is_unique:
            raise ValueError("Duplicate timestamps")

        output_path = (
            output_dir / f"de_lu_{name}_2024_test.parquet"
        )

        data.to_parquet(output_path)

        print("Rows:", len(data))
        print("Columns:", data.columns.tolist())
        print("Missing values:")
        print(data.isna().sum())
        print("Interval distribution:")
        print(data.index.to_series().diff().value_counts().head())
        print("First rows:")
        print(data.head())
        print("Saved:", output_path)

    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}")
