
"""Historical day-ahead electricity price forecasting pipeline."""

from pathlib import Path
from datetime import date, timedelta
import json

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"

TIMEZONE = "Europe/Berlin"

model = joblib.load(
    MODEL_DIR / "enriched_xgboost.joblib"
)

with open(MODEL_DIR / "enriched_features.json") as f:
    FEATURES = json.load(f)


def forecast_day(delivery_date: str) -> pd.DataFrame:
    """Forecast prices for one historical German delivery day."""

    target = date.fromisoformat(delivery_date)

    # Load historical prices and market forecasts
    prices = pd.read_parquet(
        DATA_DIR / "germany_luxembourg_analytics.parquet"
    )

    market = pd.read_parquet(
        DATA_DIR / "germany_luxembourg_market_features.parquet"
    )

    # Build exact local delivery-day boundaries
    start_local = pd.Timestamp(target, tz=TIMEZONE)
    end_local = pd.Timestamp(
        target + timedelta(days=1), tz=TIMEZONE
    )

    start_utc = start_local.tz_convert("UTC")
    end_utc = end_local.tz_convert("UTC")

    # Select forecast inputs for the delivery day
    day_market = market.loc[
        (market.index >= start_utc)
        & (market.index < end_utc)
    ].copy()

    expected_hours = pd.date_range(
        start=start_utc,
        end=end_utc,
        freq="h",
        inclusive="left"
    )

    # Compare timestamps using matching precision
    expected_hours = expected_hours.as_unit("us")

    if not day_market.index.equals(expected_hours):
        raise ValueError(
            "Incomplete hourly market forecast coverage"
        )

    if day_market.isna().any().any():
        raise ValueError(
            "Missing market forecast inputs for this date"
        )

    # Assume prediction issued at 09:00 on D-1.
    # Use the last fully completed local day: D-2.
    history_day = target - timedelta(days=2)

    local_dates = prices.index.tz_convert(
        TIMEZONE
    ).date

    history = prices.loc[
        local_dates == history_day,
        "price_eur_mwh"
    ]

    if len(history) not in (23, 24, 25):
        raise ValueError(
            "Incomplete historical price data"
        )

    local_hours = day_market.index.tz_convert(TIMEZONE)

    # Calendar features
    day_market["hour"] = local_hours.hour
    day_market["day_of_week"] = local_hours.day_of_week
    day_market["month"] = local_hours.month

    # Historical price statistics
    day_market["known_daily_mean"] = history.mean()
    day_market["known_daily_min"] = history.min()
    day_market["known_daily_max"] = history.max()
    day_market["known_daily_std"] = history.std()

    # Electricity market features
    load = day_market["load_forecast_mw"]
    wind = day_market["wind_forecast_mw"]
    solar = day_market["solar_forecast_mw"]

    if (load <= 0).any():
        raise ValueError("Invalid load forecast values")

    day_market["residual_load_mw"] = (
        load - wind - solar
    )

    day_market["renewable_share"] = (
        wind + solar
    ) / load

    day_market["wind_load_ratio"] = wind / load

    # Verify model inputs
    X = day_market[FEATURES].replace(
        [np.inf, -np.inf], np.nan
    )

    if X.isna().any().any():
        raise ValueError("Invalid model features")

    # Generate hourly price predictions
    day_market["predicted_price_eur_mwh"] = (
        model.predict(X)
    )

    return day_market[
        [
            "predicted_price_eur_mwh",
            "load_forecast_mw",
            "wind_forecast_mw",
            "solar_forecast_mw"
        ]
    ]
