
# EU Power & Gas Market Monitor

### Electricity Price Forecasting, Market Analytics & Model Evaluation

A full-stack energy market analytics application built with **Python, XGBoost, FastAPI, React, and TypeScript**.

The platform analyzes historical German–Luxembourg (DE-LU) day-ahead electricity prices, generates hourly price predictions, evaluates model accuracy, and presents market insights through an interactive dashboard.

> **Project status:** Functional historical electricity market forecasting prototype. Gas, carbon, and weather integration are planned extensions.

## Features

### 1. Electricity Price Forecasting
- Predicts hourly DE-LU electricity prices in EUR/MWh.
- Uses an XGBoost regression model.
- Incorporates historical price statistics, calendar features, electricity demand forecasts, and wind/solar generation forecasts.
- Supports German local delivery days of 23, 24, or 25 hours during daylight-saving transitions.

### 2. Interactive Forecast Dashboard
- Daily electricity price forecasts.
- Average, minimum, and maximum predicted prices.
- Electricity demand, wind, and solar generation charts.
- Identification of predicted price spikes and negative-price hours.
- Cheapest and most expensive forecast hours.

### 3. Market Intelligence
- Automated, evidence-based explanations of forecast patterns.
- Comparisons of demand and renewable generation between selected hours.
- Price spread analysis.
- Explicit separation of observed relationships from proven causes.

Market explanations are currently generated using deterministic Python calculations and templates, rather than an autonomous AI agent.

### 4. Accuracy & Backtesting
- Historical evaluation against observed electricity prices.
- XGBoost comparison with a simple historical-price baseline.
- Monthly mean absolute error (MAE) analysis.
- Interactive actual-versus-predicted price charts.
- Date-level inspection of historical predictions.

## Historical Model Evaluation

Evaluation period: **3 January – 31 December 2025**

| Metric | XGBoost | Historical Baseline |
|---|---:|---:|
| MAE | €14.87/MWh | €32.80/MWh |
| RMSE | €23.62/MWh | €49.51/MWh |

**Additional results:**
- 363 delivery days evaluated.
- 8,712 hourly predictions.
- 54.7% lower MAE compared with the baseline.

These are historical replay results, not verified live forecasting results.

### Important Evaluation Limitations

Original publication timestamps of historical load, wind, and solar forecasts have not yet been verified against the assumed prediction cutoff.

Therefore, the evaluation cannot currently be described as fully leakage-free or as proven real-world day-ahead performance.

The evaluation also includes limited interpolation of missing forecast inputs and daylight-saving adjustments in the baseline.

The reported accuracy should be interpreted with these limitations in mind.

## Technology Stack

| Layer | Technologies |
|---|---|
| Data ingestion | Python, Pandas, ENTSO-E API |
| Data storage | Parquet |
| Feature engineering | Pandas, NumPy |
| Machine learning | XGBoost, scikit-learn |
| Model persistence | Joblib |
| Backend API | FastAPI, Pydantic |
| Frontend | React, TypeScript, Vite |
| Styling | Tailwind CSS |
| Visualization | Recharts |
| Development | Jupyter Notebook, Git, GitHub |

## System Architecture

```text
ENTSO-E Historical Market Data
              |
              v
     Data Ingestion
              |
              v
    Cleaning & Validation
              |
              v
      Feature Engineering
              |
              v
       XGBoost Model
              |
       +------+------+
       |             |
       v             v
  Forecasting     Backtesting
       |             |
       +------+------+
              |
              v
          FastAPI
              |
              v
       React Dashboard
              |
      +-------+--------+
      |                |
      v                v
Forecast Dashboard   Accuracy &
                     Backtesting
```

## Data Sources

### ENTSO-E Transparency Platform

Historical data includes:

- German–Luxembourg day-ahead electricity prices.
- Electricity load forecasts.
- Wind generation forecasts.
- Solar generation forecasts.

Source: https://transparency.entsoe.eu/

### Historical Coverage

The underlying electricity price dataset covers 2023–2025, with 26,304 hourly observations after processing.

The 2025 dataset is used for historical model evaluation, with the model trained on earlier years.

## Running the Application Locally

### Prerequisites

- Python environment with the project's required dependencies.
- Node.js and npm.
- Historical datasets and trained model artifacts.

Some data and model files are not committed to GitHub. They must be generated or made available locally before the forecasting API can run.

### 1. Clone the Repository

```bash
git clone https://github.com/rahatmulla/EU-Power-Gas-Market-Monitor.git
cd EU-Power-Gas-Market-Monitor
```

### 2. Set Up the Python Environment

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies required by the ingestion, forecasting, and API modules.

Configure your ENTSO-E API credentials in a local `.env` file when downloading market data.

Never commit API keys or other secrets.

### 3. Start FastAPI

From the project root:

```powershell
uvicorn src.api.main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

### 4. Start React

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

http://localhost:5173

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API health message |
| POST | `/forecast/predict` | Price prediction from supplied features |
| GET | `/forecast/day` | Historical hourly forecast |
| GET | `/forecast/day/explanation` | Evidence-based market explanation |
| GET | `/forecast/backtest` | Historical model evaluation results |

Example:

```http
GET /forecast/day?delivery_date=2025-07-15
```

The `/forecast/backtest` endpoint is available in the local application after registering the backtesting router.

## Future Improvements

- Integrate TTF natural gas prices.
- Incorporate EU ETS carbon allowance prices.
- Add temperature and weather forecast data.
- Verify historical forecast publication vintages.
- Strengthen leakage-safe walk-forward evaluation.
- Improve data and model reproducibility.
- Add automated tests and CI.
- Deploy the frontend and backend.

## Project Objective

This project demonstrates practical skills in:

- European electricity market data analysis.
- Time-series forecasting and feature engineering.
- Model evaluation and benchmarking.
- Energy market fundamentals.
- API development and frontend visualization.
- Translating analytical results into usable market intelligence.

The objective is to build an explainable and testable energy market research tool, rather than a black-box trading system.

## Disclaimer

This project is for research, education, and portfolio demonstration purposes only. It does not provide live trading signals, financial advice, or guaranteed electricity price forecasts.

## Author

**Rahat Mulla**

GitHub: https://github.com/rahatmulla

Portfolio: https://rahatmulla.github.io/
