
"""Read historical forecasting evaluation results."""

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/forecast", tags=["Backtesting"])

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "data" / "processed" / "forecast_backtest_2025.csv"


@router.get("/backtest")
def get_backtest():
    if not CSV_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Backtest CSV not found. Run the evaluation script first.",
        )

    df = pd.read_csv(CSV_PATH, parse_dates=["timestamp_utc"])

    required = {
        "timestamp_utc",
        "delivery_date",
        "actual",
        "predicted",
        "baseline",
    }

    if not required.issubset(df.columns):
        raise HTTPException(
            status_code=422,
            detail=f"Missing CSV columns: {sorted(required - set(df.columns))}",
        )

    if df.empty or df[list(required)].isna().any().any():
        raise HTTPException(
            status_code=422,
            detail="Backtest CSV contains missing values or no data.",
        )

    df["absolute_error"] = (df["actual"] - df["predicted"]).abs()
    df["baseline_absolute_error"] = (
        df["actual"] - df["baseline"]
    ).abs()

    model_mae = float(df["absolute_error"].mean())
    baseline_mae = float(df["baseline_absolute_error"].mean())

    df["month"] = df["delivery_date"].str.slice(0, 7)

    monthly = (
        df.groupby("month")
        .agg(
            hours=("actual", "size"),
            model_mae=("absolute_error", "mean"),
            baseline_mae=("baseline_absolute_error", "mean"),
        )
        .reset_index()
        .round(2)
    )

    hourly = df[
        ["timestamp_utc", "delivery_date", "actual", "predicted", "baseline"]
    ].copy()

    hourly["timestamp_utc"] = hourly["timestamp_utc"].dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    return {
        "forecast_type": "historical_replay",
        "publication_vintage_verified": False,
        "year": 2025,
        "summary": {
            "days_evaluated": int(df["delivery_date"].nunique()),
            "hours_evaluated": len(df),
            "model_mae": round(model_mae, 2),
            "baseline_mae": round(baseline_mae, 2),
            "improvement_percent": round(
                (baseline_mae - model_mae) / baseline_mae * 100, 1
            ) if baseline_mae else None,
        },
        "monthly": monthly.to_dict(orient="records"),
        "hourly": hourly.to_dict(orient="records"),
    }
