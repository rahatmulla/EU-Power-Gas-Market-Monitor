"""Prepare factual evidence for electricity market explanations."""

import pandas as pd


def build_market_evidence(forecast: pd.DataFrame) -> dict:
    """Summarize predicted prices and forecast market conditions for one day."""
    required = {
        "predicted_price_eur_mwh",
        "solar_forecast_mw",
        "wind_forecast_mw",
        "load_forecast_mw",
    }
    missing = required.difference(forecast.columns)
    if missing:
        raise ValueError(f"Missing forecast columns: {', '.join(sorted(missing))}")
    if forecast.empty:
        raise ValueError("Cannot explain an empty forecast")
    if forecast[list(required)].isna().any().any():
        raise ValueError("Cannot explain a forecast with missing market values")
    if not isinstance(forecast.index, pd.DatetimeIndex) or forecast.index.tz is None:
        raise ValueError("Forecast must have a timezone-aware DatetimeIndex")

    prices = forecast["predicted_price_eur_mwh"]
    cheapest = prices.idxmin()
    expensive = prices.idxmax()

    def local_hour(timestamp):
        return timestamp.tz_convert("Europe/Berlin").strftime("%H:%M")

    def at(column, timestamp):
        return round(float(forecast.loc[timestamp, column]), 2)

    return {
        "cheapest_hour": local_hour(cheapest),
        "cheapest_price_eur_mwh": round(float(prices.min()), 2),
        "most_expensive_hour": local_hour(expensive),
        "highest_price_eur_mwh": round(float(prices.max()), 2),
        "price_spread_eur_mwh": round(float(prices.max() - prices.min()), 2),
        "solar_at_cheapest_hour_mw": at("solar_forecast_mw", cheapest),
        "solar_at_expensive_hour_mw": at("solar_forecast_mw", expensive),
        "wind_at_cheapest_hour_mw": at("wind_forecast_mw", cheapest),
        "wind_at_expensive_hour_mw": at("wind_forecast_mw", expensive),
        "demand_at_cheapest_hour_mw": at("load_forecast_mw", cheapest),
        "demand_at_expensive_hour_mw": at("load_forecast_mw", expensive),
    }


def build_market_changes(evidence: dict) -> dict:
    """Compare forecast conditions at the highest- and lowest-price hours."""

    def compare(name):
        cheap = evidence[f"{name}_at_cheapest_hour_mw"]
        expensive = evidence[f"{name}_at_expensive_hour_mw"]
        change = round(expensive - cheap, 2)
        direction = "increased" if change > 0 else "decreased" if change < 0 else "unchanged"
        return {"direction": direction, "change_mw": change, "unit": "MW"}

    return {
        "solar": compare("solar"),
        "wind": compare("wind"),
        "demand": compare("demand"),
    }
