
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EU Market Monitor API",
    description="Germany–Luxembourg electricity market intelligence",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "germany_luxembourg_analytics.parquet"
)


def load_data():
    if not DATA_PATH.exists():
        raise RuntimeError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_parquet(DATA_PATH).sort_index()

    if "timestamp_local" not in df.columns:
        df["timestamp_local"] = df.index.tz_convert(
            "Europe/Berlin"
        )

    df["year"] = df["timestamp_local"].dt.year
    df["hour"] = df["timestamp_local"].dt.hour

    return df


df = load_data()


def filter_data(year: Optional[int]):
    if year is None:
        return df
    result = df[df["year"] == year]
    if result.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No data available for year {year}",
        )
    return result


@app.get("/")
def root():
    return {
        "application": "EU Market Monitor",
        "status": "running",
    }


@app.get("/api/market/summary")
def market_summary(year: Optional[int] = None):
    data = filter_data(year)
    prices = data["price_eur_mwh"]

    return {
        "observations": len(data),
        "average_price": round(float(prices.mean()), 2),
        "minimum_price": round(float(prices.min()), 2),
        "maximum_price": round(float(prices.max()), 2),
        "price_std": round(float(prices.std()), 2),
        "negative_price_hours": int((prices < 0).sum()),
        "anomaly_hours": int(data["is_anomaly"].sum()),
    }


@app.get("/api/market/prices")
def market_prices(
    year: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=10000),
):
    data = filter_data(year).tail(limit)

    return [
        {
            "timestamp": timestamp.isoformat(),
            "price_eur_mwh": float(row["price_eur_mwh"]),
        }
        for timestamp, row in data.iterrows()
    ]


@app.get("/api/market/hourly-pattern")
def hourly_pattern(year: Optional[int] = None):
    data = filter_data(year)

    hourly = (
        data.groupby("hour")["price_eur_mwh"]
        .mean()
        .round(2)
    )

    return [
        {"hour": int(hour), "average_price": float(price)}
        for hour, price in hourly.items()
    ]


@app.get("/api/market/negative-prices")
def negative_prices(year: Optional[int] = None):
    data = filter_data(year)
    negative = data[data["price_eur_mwh"] < 0]

    by_hour = negative.groupby("hour").size()

    return {
        "total": len(negative),
        "percentage": round(
            len(negative) / len(data) * 100, 2
        ),
        "hourly_distribution": [
            {
                "hour": hour,
                "count": int(by_hour.get(hour, 0)),
            }
            for hour in range(24)
        ],
    }


@app.get("/api/market/anomalies")
def market_anomalies(
    year: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=1000),
):
    data = filter_data(year)
    anomalies = data[data["is_anomaly"]]

    anomalies = anomalies.sort_values(
        "abs_price_change", ascending=False
    ).head(limit)

    return {
        "total": int(data["is_anomaly"].sum()),
        "events": [
            {
                "timestamp": timestamp.isoformat(),
                "price": float(row["price_eur_mwh"]),
                "price_change": float(row["price_change"]),
                "absolute_change": float(
                    row["abs_price_change"]
                ),
            }
            for timestamp, row in anomalies.iterrows()
        ],
    }
