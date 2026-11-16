# EU Power & Gas Market Monitor — System Architecture

## 1. Project Overview

The EU Power & Gas Market Monitor is a Python-based electricity market analytics and forecasting application with a React frontend.

Its primary focus is the Germany–Luxembourg (DE-LU) day-ahead electricity market.

The application combines historical electricity prices, market fundamentals, machine learning, and AI-generated explanations to help users understand electricity price movements and explore forecasts.

## 2. High-Level Architecture

```text
ENTSO-E Market Data
        |
        v
Data Ingestion (Python)
        |
        v
Data Processing & Validation
        |
        v
Feature Engineering
        |
        v
Machine Learning (XGBoost)
        |
        v
Forecasting & Intelligence
        |
        v
FastAPI Backend
        |
        v
React Dashboard
```

The system separates data collection, processing, forecasting, backend services, and presentation into distinct layers.

## 3. Technology Stack

| Layer | Technologies | Purpose |
|---|---|---|
| Frontend | React, TypeScript, Vite | Interactive market dashboard |
| Backend | Python, FastAPI, Pydantic | API endpoints and input validation |
| Data ingestion | Python, pandas, ENTSO-E API | Download electricity market data |
| Data processing | pandas, NumPy, Parquet | Clean, validate, and prepare datasets |
| Machine learning | XGBoost, scikit-learn | Train and evaluate forecasting models |
| Model persistence | joblib, JSON | Store trained models and feature metadata |
| AI intelligence | LLM-based explanation module | Generate market explanations |
| Research | Jupyter Notebook, Matplotlib | Exploratory analysis and experimentation |

## 4. Repository Structure

### `src/ingestion/`

Contains scripts responsible for downloading market data, including historical electricity prices and available market forecasts.

### `src/processing/`

Contains scripts for repairing, validating, and transforming raw market data into analysis-ready datasets.

### `src/forecasting/`

Contains feature engineering, model training, forecasting pipelines, market intelligence, and explanation logic.

Important modules include:

- `features.py` — forecasting feature construction.
- `pipeline.py` — forecasting pipeline.
- `train_model.py` — earlier model training implementation.
- `intelligence.py` — market intelligence calculations.
- `explanations.py` — explanation-related logic.
- `ai_explainer.py` — AI-assisted explanation functionality.

### `src/api/`

Contains the FastAPI application and API routers.

- `main.py` — application entry point.
- `forecasting.py` — forecasting API functionality.
- `market.py` — historical market data endpoints in the local integrated application.

### `frontend/`

Contains the React and TypeScript dashboard, including its UI components, charts, and API integration.

### `notebooks/`

Contains research and experimentation:

1. `01_electricity_price_eda.ipynb` — exploratory data analysis.
2. `02_forecasting_experiments.ipynb` — forecasting model experiments.
3. `03_enriched_forecasting.ipynb` — enriched model analysis and export.

### `data/`

Stores raw and processed datasets used by the analysis and forecasting pipelines.

### `models/`

Stores serialized model artifacts and model feature metadata.

## 5. Data and Forecasting Workflow

**Stage 1 — Ingestion**

Download historical market prices and relevant electricity market forecasts from external data sources.

**Stage 2 — Processing**

Validate timestamps, handle missing observations, standardize data formats, and prepare hourly datasets.

**Stage 3 — Feature Engineering**

Construct model inputs from historical prices, calendar information, electricity demand, and renewable generation forecasts.

**Stage 4 — Model Development**

Compare forecasting approaches using historical data and time-aware evaluation. Analyze errors, particularly during negative prices and price spikes.

**Stage 5 — Forecast Generation**

Use trained model artifacts and compatible feature inputs to produce electricity price forecasts.

**Stage 6 — Intelligence**

Analyze market conditions and generate explanatory insights using calculated indicators and AI-assisted interpretation.

**Stage 7 — API and Dashboard**

Expose forecasts and market information through FastAPI endpoints and present them in the React application.

## 6. Important Engineering Considerations

### Time zones and daylight saving

Germany observes daylight saving time, so local electricity delivery days may contain 23, 24, or 25 hours.

Timestamp handling must preserve the correct relationship between UTC and the Europe/Berlin time zone.

### Data leakage

Forecasting inputs must represent information that would have been available at the time the forecast was issued. Future realized market prices must not be used as predictive inputs.

### Model evaluation

Model performance should be evaluated using chronological splits or walk-forward backtesting rather than random splitting.

### Extreme market conditions

Average model accuracy alone may hide poor performance during negative-price events and large price spikes. These conditions should be assessed separately.

## 7. Application Boundaries

The current application is a market analytics and forecasting prototype, not an automated electricity trading system.

Forecasts and AI explanations support analysis and should not be interpreted as guaranteed market outcomes.

## 8. Future Improvements

- Automated ingestion and scheduled data refreshes.
- Improved forecasting evaluation and model monitoring.
- Additional gas, carbon, weather, and storage fundamentals.
- More modular React dashboard components.
- Automated testing and deployment workflows.

These are potential improvements, not claims of currently implemented functionality.
