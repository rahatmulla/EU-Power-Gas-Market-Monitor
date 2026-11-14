
from pathlib import Path

import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import joblib

from src.forecasting.features import create_features

# Define dataset and model storage paths
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "processed" / "germany_luxembourg_analytics.parquet"
MODEL_PATH = ROOT / "models" / "electricity_price_model.joblib"

# 1. Load historical electricity data and create forecasting features
df = pd.read_parquet(DATA_PATH)
features = create_features(df)

# 2. Separate input features from the electricity price target
target = "price_eur_mwh"
X = features.drop(columns=[target])
y = features[target]

# 3. Train on 2023–2024 data and test on 2025 data
train_mask = features.index.year <= 2024
test_mask = features.index.year == 2025

X_train, X_test = X.loc[train_mask], X.loc[test_mask]
y_train, y_test = y.loc[train_mask], y.loc[test_mask]

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))

# 4. Train the machine learning model
model = HistGradientBoostingRegressor(
    max_iter=300,
    learning_rate=0.05,
    max_leaf_nodes=31,
    random_state=42
)

model.fit(X_train, y_train)

# 5. Predict electricity prices and measure accuracy
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))

# 6. Compare model accuracy against yesterday's electricity prices
baseline = X_test["lag_24"]
baseline_mae = mean_absolute_error(y_test, baseline)

print(f"\nModel MAE: €{mae:.2f}/MWh")
print(f"Model RMSE: €{rmse:.2f}/MWh")
print(f"Baseline MAE: €{baseline_mae:.2f}/MWh")

# 7. Save the trained model for future predictions
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_PATH)

print(f"\nModel saved to: {MODEL_PATH}")
