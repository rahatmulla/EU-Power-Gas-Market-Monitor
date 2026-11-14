
"""Generate market intelligence from hourly price forecasts."""

import pandas as pd


def analyze_forecast(forecast: pd.DataFrame) -> dict:
    prices = forecast["predicted_price_eur_mwh"]

    cheapest = prices.idxmin()
    most_expensive = prices.idxmax()

    spike_hours = prices[prices > 150]
    negative_hours = prices[prices < 0]

    def local_time(timestamp):
        return timestamp.tz_convert(
            "Europe/Berlin"
        ).isoformat()

    return {
        "cheapest_hour": {
            "timestamp_local": local_time(cheapest),
            "price_eur_mwh": round(float(prices.min()), 2),
        },
        "most_expensive_hour": {
            "timestamp_local": local_time(most_expensive),
            "price_eur_mwh": round(float(prices.max()), 2),
        },
        "daily_price_spread": round(
            float(prices.max() - prices.min()), 2
        ),
        "spike_hours": [
            {
                "timestamp_local": local_time(timestamp),
                "price_eur_mwh": round(float(price), 2),
            }
            for timestamp, price in spike_hours.items()
        ],
        "negative_price_hours": [
            {
                "timestamp_local": local_time(timestamp),
                "price_eur_mwh": round(float(price), 2),
            }
            for timestamp, price in negative_hours.items()
        ],
    }
