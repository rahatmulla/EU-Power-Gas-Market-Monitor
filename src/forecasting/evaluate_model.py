
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.forecasting.pipeline import forecast_day

PRICES_PATH = "data/processed/germany_luxembourg_analytics.parquet"
TIMEZONE = "Europe/Berlin"

# Load actual historical electricity prices
prices = pd.read_parquet(PRICES_PATH)["price_eur_mwh"]
prices.index = prices.index.tz_convert("UTC")
prices = prices.sort_index()

results = []
failed_days = []
baseline_adjustments = []


def get_baseline(forecast_index):
    """
    D-2 baseline using the same German local clock hour.

    During daylight-saving transitions:
    - Missing hour: use the last valid instant before the gap.
    - Repeated hour: match the occurrence where possible.
    """
    local_hours = forecast_index.tz_convert(TIMEZONE)
    baseline_values = []

    for timestamp in local_hours:
        target_date = (
            timestamp.date() - pd.Timedelta(days=2)
        )

        naive_target = pd.Timestamp(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day,
            hour=timestamp.hour,
        )

        # Identify the occurrence of a repeated hour.
        # fold=0: first occurrence; fold=1: second occurrence.
        occurrence = timestamp.fold

        try:
            baseline_time = naive_target.tz_localize(
                TIMEZONE,
                ambiguous=(occurrence == 0),
                nonexistent="raise",
            )

        except ValueError:
            # Spring clock change: the requested hour doesn't exist.
            baseline_time = naive_target.tz_localize(
                TIMEZONE,
                ambiguous=(occurrence == 0),
                nonexistent="shift_forward",
            )

            baseline_adjustments.append(
                (str(timestamp), str(baseline_time))
            )

        baseline_utc = baseline_time.tz_convert("UTC")
        baseline_values.append(prices.get(baseline_utc, np.nan))

    return pd.Series(
        baseline_values,
        index=forecast_index,
        dtype=float,
    )


# Evaluate January 3 through December 31, 2025
for day in pd.date_range("2025-01-03", "2025-12-31"):
    date_str = day.strftime("%Y-%m-%d")

    try:
        forecast = forecast_day(date_str)

        actual = prices.reindex(forecast.index)
        baseline = get_baseline(forecast.index)

        if actual.isna().any() or baseline.isna().any():
            raise ValueError("Missing actual or baseline prices")

        results.append(
            pd.DataFrame({
                "timestamp_utc": forecast.index,
                "delivery_date": date_str,
                "actual": actual.to_numpy(),
                "predicted": forecast[
                    "predicted_price_eur_mwh"
                ].to_numpy(),
                "baseline": baseline.to_numpy(),
            })
        )

    except (ValueError, KeyError, FileNotFoundError) as exc:
        failed_days.append((date_str, str(exc)))


if not results:
    raise RuntimeError("No days could be evaluated")


df = pd.concat(results, ignore_index=True)

from pathlib import Path

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "forecast_backtest_2025.csv"

df["absolute_error"] = (
    df["actual"] - df["predicted"]
).abs()

df["baseline_absolute_error"] = (
    df["actual"] - df["baseline"]
).abs()

df.to_csv(OUTPUT_PATH, index=False)

print(f"\nBacktest results saved: {OUTPUT_PATH}")
print(f"Rows exported: {len(df)}")


def metrics(predictions):
    mae = mean_absolute_error(
        df["actual"],
        predictions,
    )

    rmse = np.sqrt(
        mean_squared_error(
            df["actual"],
            predictions,
        )
    )

    return mae, rmse


model_mae, model_rmse = metrics(df["predicted"])
baseline_mae, baseline_rmse = metrics(df["baseline"])

improvement = (
    (baseline_mae - model_mae) / baseline_mae * 100
    if baseline_mae != 0
    else np.nan
)


print("\n2025 EVALUATION")
print("-" * 45)

print("Hours evaluated:", len(df))
print("Days evaluated:", len(results))
print("Days failed:", len(failed_days))

print(f"\nXGBoost MAE:    {model_mae:.2f} EUR/MWh")
print(f"XGBoost RMSE:   {model_rmse:.2f} EUR/MWh")

print(f"\nBaseline MAE:   {baseline_mae:.2f} EUR/MWh")
print(f"Baseline RMSE:  {baseline_rmse:.2f} EUR/MWh")

print(f"\nMAE improvement: {improvement:.1f}%")

print("\nDST adjustments:", len(baseline_adjustments))

if baseline_adjustments:
    for original, adjusted in baseline_adjustments:
        print(f"  {original} -> {adjusted}")

if failed_days:
    print("\nFailed days:")
    for day, error in failed_days:
        print(day, error)
else:
    print("\nAll evaluation days passed.")
