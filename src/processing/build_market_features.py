
"""Build hourly market features from ENTSO-E forecasts."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = ROOT / "data" / "raw" / "entsoe"
OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset(name):
    files = sorted(
        RAW_DIR.glob(f"de_lu_{name}_20??_??.parquet")
    )

    if len(files) != 36:
        raise ValueError(
            f"Expected 36 files for {name}, found {len(files)}"
        )

    data = pd.concat(
        [pd.read_parquet(f) for f in files]
    ).sort_index()

    if not data.index.is_unique:
        raise ValueError(f"Duplicate timestamps in {name}")

    return data


load = load_dataset("load_forecast")
renewables = load_dataset("wind_solar_forecast")

# Align both datasets to a complete 15-minute UTC timeline
expected = pd.date_range(
    start=pd.Timestamp("2023-01-01", tz="Europe/Berlin").tz_convert("UTC"),
    end=pd.Timestamp("2026-01-01", tz="Europe/Berlin").tz_convert("UTC"),
    freq="15min",
    inclusive="left"
)

load = load.reindex(expected)
renewables = renewables.reindex(expected)

# Hourly averages, requiring all four quarter-hour values
load_hourly = load.resample("h").mean()

renewables_hourly = renewables.resample("h").mean()

load_counts = load.resample("h").count()
renewable_counts = renewables.resample("h").count()

# Require four valid observations per hourly feature
market = pd.DataFrame(index=load_hourly.index)

market["load_forecast_mw"] = (
    load_hourly["Forecasted Load"].where(
        load_counts["Forecasted Load"] == 4
    )
)

market["solar_forecast_mw"] = (
    renewables_hourly["Solar"].where(
        renewable_counts["Solar"] == 4
    )
)

wind_onshore = renewables_hourly["Wind Onshore"].where(
    renewable_counts["Wind Onshore"] == 4
)

wind_offshore = renewables_hourly["Wind Offshore"].where(
    renewable_counts["Wind Offshore"] == 4
)

market["wind_forecast_mw"] = (
    wind_onshore + wind_offshore
)

# Preserve missing values for later review
output_path = (
    OUTPUT_DIR / "germany_luxembourg_market_features.parquet"
)

market.index.name = "timestamp_utc"
market.to_parquet(output_path)

print("Dataset shape:", market.shape)
print("\nMissing values:")
print(market.isna().sum())

print("\nRows with missing values:")
print(market[market.isna().any(axis=1)])

print("\nSaved:", output_path)
