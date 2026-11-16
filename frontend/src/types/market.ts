export type ForecastHour = {
  timestamp_utc: string;
  timestamp_local: string;
  predicted_price_eur_mwh: number;
  load_forecast_mw: number;
  wind_forecast_mw: number;
  solar_forecast_mw: number;
};

export type PriceEvent = {
  timestamp_local: string;
  price_eur_mwh: number;
};

export type ForecastData = {
  delivery_date: string;
  market: string;
  model: string;
  forecast_type: string;
  publication_vintage_verified: boolean;
  hours: ForecastHour[];
  summary: {
    average_price: number;
    minimum_price: number;
    maximum_price: number;
    negative_price_hours: number;
  };
  intelligence: {
    cheapest_hour: PriceEvent;
    most_expensive_hour: PriceEvent;
    daily_price_spread: number;
    spike_hours: PriceEvent[];
    negative_price_hours: PriceEvent[];
  };
};

export type ExplanationData = {
  delivery_date: string;
  explanation: string;
  generated_by: string;
  analysis_type: string;
};

export type ChartHour = {
  time: string;
  price: number;
  load: number;
  wind: number;
  solar: number;
};

export const formatHour = (timestamp: string) => timestamp.slice(11, 16);
export const euro = (value: number) => `€${value.toFixed(2)}`;
