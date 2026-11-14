from pathlib import Path

import pandas as pd

from src.forecasting.features import create_features

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "germany_luxembourg_analytics.parquet"
)

df = pd.read_parquet(DATA_PATH)

features = create_features(df)

print("Feature dataset shape:", features.shape)
print("\nColumns:")
print(features.columns.tolist())

print("\nFirst five rows:")
print(features.head())

print("\nMissing values:")
print(features.isna().sum())