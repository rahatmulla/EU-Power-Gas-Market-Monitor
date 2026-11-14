"""Build the forecasting feature engineering pipeline for EU Market Monitor."""

import numpy as np
import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create features for 24-hour-ahead electricity
    price forecasting.

    Each row represents a target hour.
    Historical price features are drawn from
    at least 24 hours before that target.
    """
    data = df[["price_eur_mwh"]].copy()
    data = data.sort_index()

    # Use UTC for consistent hourly lag calculations
    if data.index.tz is None:
        raise ValueError("Expected timezone-aware UTC index")

    if not data.index.is_unique:
        raise ValueError("Duplicate timestamps found")

    # Calendar features in Germany local time
    local_time = data.index.tz_convert("Europe/Berlin")

    data["hour"] = local_time.hour
    data["day_of_week"] = local_time.dayofweek
    data["month"] = local_time.month
    data["is_weekend"] = (
        local_time.dayofweek >= 5
    ).astype(int)

    # Cyclical calendar features
    data["hour_sin"] = np.sin(
        2 * np.pi * data["hour"] / 24
    )
    data["hour_cos"] = np.cos(
        2 * np.pi * data["hour"] / 24
    )

    # Historical price lags
    for lag in [24, 48, 168]:
        data[f"lag_{lag}"] = (
            data["price_eur_mwh"].shift(lag)
        )

    # Historical rolling statistics
    # Shift first to avoid future information
    history = data["price_eur_mwh"].shift(24)

    data["rolling_mean_24"] = (
        history.rolling(24).mean()
    )

    data["rolling_std_24"] = (
        history.rolling(24).std()
    )

    # Remove rows without sufficient history
    data = data.dropna()

    return data
