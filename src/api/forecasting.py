
from pathlib import Path
import json

import joblib
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models"

model = joblib.load(
    MODEL_DIR / "enriched_xgboost.joblib"
)

with open(MODEL_DIR / "enriched_features.json") as f:
    FEATURES = json.load(f)


class ForecastInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    month: int = Field(ge=1, le=12)

    known_daily_mean: float
    known_daily_min: float
    known_daily_max: float
    known_daily_std: float = Field(ge=0)

    load_forecast_mw: float = Field(ge=0)
    solar_forecast_mw: float = Field(ge=0)
    wind_forecast_mw: float = Field(ge=0)

    residual_load_mw: float
    renewable_share: float = Field(ge=0)
    wind_load_ratio: float = Field(ge=0)


def predict_price(payload: ForecastInput) -> float:
    values = payload.model_dump()

    frame = pd.DataFrame(
        [{name: values[name] for name in FEATURES}],
        columns=FEATURES,
    )

    return float(model.predict(frame)[0])
