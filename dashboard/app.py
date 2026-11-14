
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="EU Market Monitor",
    page_icon="⚡",
    layout="wide",
)

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "germany_luxembourg_analytics.parquet"
)


@st.cache_data
def load_data():
    data = pd.read_parquet(DATA_PATH)
    data = data.sort_index()

    if "timestamp_local" not in data.columns:
        data["timestamp_local"] = (
            data.index.tz_convert("Europe/Berlin")
        )

    data["year"] = data["timestamp_local"].dt.year
    return data


df = load_data()

st.title("⚡ EU Market Monitor")
st.caption(
    "Germany–Luxembourg | Historical Day-Ahead Electricity Market"
)

# Sidebar filters
st.sidebar.header("Market Filters")

years = sorted(df["year"].unique().tolist())
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=years,
    default=years,
)

filtered = df[df["year"].isin(selected_years)].copy()

if filtered.empty:
    st.warning("Select at least one year.")
    st.stop()

# KPI metrics
st.subheader("Market Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Average Price",
    f"€{filtered['price_eur_mwh'].mean():.2f}/MWh",
)

c2.metric(
    "Maximum Price",
    f"€{filtered['price_eur_mwh'].max():.2f}/MWh",
)

c3.metric(
    "Negative-Price Hours",
    f"{(filtered['price_eur_mwh'] < 0).sum():,}",
)

c4.metric(
    "Anomalous Hours",
    f"{filtered['is_anomaly'].sum():,}",
)

# Daily price trend
st.subheader("Daily Average Electricity Price")

daily = (
    filtered["price_eur_mwh"]
    .resample("D")
    .mean()
    .reset_index()
)

fig = px.line(
    daily,
    x="timestamp_utc",
    y="price_eur_mwh",
    labels={
        "timestamp_utc": "Date (UTC)",
        "price_eur_mwh": "Price (EUR/MWh)",
    },
)

st.plotly_chart(fig, use_container_width=True)

# Annual comparison
st.subheader("Annual Electricity Price Comparison")

annual = (
    filtered.groupby("year")["price_eur_mwh"]
    .agg(["mean", "std", "min", "max"])
    .round(2)
)

st.dataframe(annual, use_container_width=True)

# Negative Price Monitor
st.divider()
st.subheader("Negative Electricity Price Monitor")

negative = filtered[filtered["price_eur_mwh"] < 0].copy()

n1, n2 = st.columns(2)

n1.metric("Negative-Price Hours", f"{len(negative):,}")
n2.metric(
    "Negative-Price Frequency",
    f"{len(negative) / len(filtered) * 100:.2f}%"
)

negative_by_hour = (
    negative.groupby(["year", "hour"])
    .size()
    .reset_index(name="negative_hours")
)

fig_negative = px.bar(
    negative_by_hour,
    x="hour",
    y="negative_hours",
    color="year",
    barmode="group",
    title="Negative-Price Hours by Time of Day",
    labels={
        "hour": "Hour of Day",
        "negative_hours": "Negative-Price Hours",
    },
)

st.plotly_chart(fig_negative, use_container_width=True)

# Volatility and Anomaly Monitor
st.divider()
st.subheader("Volatility & Anomaly Monitor")

v1, v2, v3 = st.columns(3)

v1.metric(
    "Price Standard Deviation",
    f"€{filtered['price_eur_mwh'].std():.2f}/MWh"
)

v2.metric(
    "Average Absolute Hourly Change",
    f"€{filtered['abs_price_change'].mean():.2f}/MWh"
)

v3.metric(
    "Detected Anomalies",
    f"{filtered['is_anomaly'].sum():,}"
)

fig_anomaly = px.line(
    filtered.reset_index(),
    x="timestamp_utc",
    y="price_eur_mwh",
    title="Electricity Prices and Anomalous Movements",
)

anomalies = filtered[filtered["is_anomaly"]].reset_index()

fig_anomaly.add_scatter(
    x=anomalies["timestamp_utc"],
    y=anomalies["price_eur_mwh"],
    mode="markers",
    name="Anomalous Hourly Change",
    marker=dict(color="red", size=6),
)

st.plotly_chart(fig_anomaly, use_container_width=True)