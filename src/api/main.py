from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api.forecasting import ForecastInput, predict_price
from src.forecasting.ai_explainer import generate_market_explanation
from src.forecasting.intelligence import analyze_forecast
from src.forecasting.pipeline import forecast_day

app = FastAPI(
    title="EU Market Monitor API",
    description="Electricity market analytics and forecasting",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ForecastResponse(BaseModel):
    predicted_price_eur_mwh: float
    model: str


@app.get("/")
def root():
    return {"message": "EU Market Monitor API is running"}


@app.post("/forecast/predict", response_model=ForecastResponse)
def forecast_predict(payload: ForecastInput):
    prediction = predict_price(payload)
    return ForecastResponse(
        predicted_price_eur_mwh=round(prediction, 2),
        model="engineered_xgboost",
    )


@app.get("/forecast/day")
def get_day_forecast(delivery_date: date):
    try:
        forecast = forecast_day(delivery_date.isoformat())
        intelligence = analyze_forecast(forecast)

        hours = []
        for timestamp, row in forecast.iterrows():
            local = timestamp.tz_convert("Europe/Berlin")
            hours.append({
                "timestamp_utc": timestamp.isoformat(),
                "timestamp_local": local.isoformat(),
                "predicted_price_eur_mwh": round(float(row["predicted_price_eur_mwh"]), 2),
                "load_forecast_mw": round(float(row["load_forecast_mw"]), 2),
                "wind_forecast_mw": round(float(row["wind_forecast_mw"]), 2),
                "solar_forecast_mw": round(float(row["solar_forecast_mw"]), 2),
            })

        return {
            "delivery_date": delivery_date.isoformat(),
            "market": "Germany-Luxembourg",
            "model": "engineered_xgboost",
            "forecast_type": "historical_replay",
            "publication_vintage_verified": False,
            "hours": hours,
            "intelligence": intelligence,
            "summary": {
                "average_price": round(float(forecast["predicted_price_eur_mwh"].mean()), 2),
                "minimum_price": round(float(forecast["predicted_price_eur_mwh"].min()), 2),
                "maximum_price": round(float(forecast["predicted_price_eur_mwh"].max()), 2),
                "negative_price_hours": int((forecast["predicted_price_eur_mwh"] < 0).sum()),
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/forecast/day/explanation")
def get_day_explanation(delivery_date: date):
    try:
        forecast = forecast_day(delivery_date.isoformat())
        result = generate_market_explanation(forecast)
        return {
            "delivery_date": delivery_date.isoformat(),
            "market": "Germany-Luxembourg",
            **result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
