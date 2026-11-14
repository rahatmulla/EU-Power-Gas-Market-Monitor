
from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

client = EntsoePandasClient(
    api_key=os.environ["ENTSOE_API_KEY"]
)

for year in [2023, 2024, 2025]:
    print(f"\n========== {year} ==========")

    start = pd.Timestamp(
        f"{year}-12-30 20:00",
        tz="UTC"
    )
    end = pd.Timestamp(
        f"{year}-12-31 04:00",
        tz="UTC"
    )

    try:
        prices = client.query_day_ahead_prices(
            country_code="DE_LU",
            start=start,
            end=end
        )

        prices.index = prices.index.tz_convert("UTC")

        print(prices.to_string())

    except Exception as exc:
        print(f"Error: {exc}")
