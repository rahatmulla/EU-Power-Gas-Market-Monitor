
"""Download historical ENTSO-E market forecasts."""

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

OUTPUT_DIR = ROOT / "data" / "raw" / "entsoe"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

datasets = {
    "load_forecast": client.query_load_forecast,
    "wind_solar_forecast": client.query_wind_and_solar_forecast,
}

for year in [2023, 2024, 2025]:
    for month in range(1, 13):

        start = pd.Timestamp(
            year=year,
            month=month,
            day=1,
            tz="Europe/Berlin"
        )
        end = start + pd.DateOffset(months=1)

        for name, query in datasets.items():

            output_path = (
                OUTPUT_DIR /
                f"de_lu_{name}_{year}_{month:02d}.parquet"
            )

            if output_path.exists():
                print(f"Skipping existing: {output_path.name}")
                continue

            print(f"Downloading {name}: {year}-{month:02d}")

            try:
                data = query(
                    country_code="DE_LU",
                    start=start,
                    end=end
                )

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

                data.to_parquet(output_path)

                print(
                    f"Saved {output_path.name} "
                    f"({len(data)} rows)"
                )

                time.sleep(2)

            except Exception as exc:
                print(
                    f"FAILED {name} {year}-{month:02d}: "
                    f"{exc}"
                )

print("\nHistorical forecast download finished.")
