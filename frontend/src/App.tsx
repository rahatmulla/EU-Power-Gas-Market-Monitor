
import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  Activity,
  AlertTriangle,
  CalendarDays,
  TrendingUp,
  TrendingDown,
  Zap,
  Lightbulb,
} from "lucide-react";

type ForecastHour = {
  timestamp_utc: string;
  timestamp_local: string;
  predicted_price_eur_mwh: number;
  load_forecast_mw: number;
  wind_forecast_mw: number;
  solar_forecast_mw: number;
};

type PriceEvent = {
  timestamp_local: string;
  price_eur_mwh: number;
};

type ForecastData = {
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

type ExplanationData = {
  delivery_date: string;
  explanation: string;
  generated_by: string;
  analysis_type: string;
};

const API_URL = "http://localhost:8000";

function formatHour(timestamp: string) {
  return timestamp.slice(11, 16);
}

function euro(value: number) {
  return `€${value.toFixed(2)}`;
}

function App() {
  const [date, setDate] = useState("2025-07-15");
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [marketExplanation, setMarketExplanation] = useState("");
  const [explanationLoading, setExplanationLoading] = useState(false);
  const [explanationError, setExplanationError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadForecast() {
      setLoading(true);
      setError("");
      setData(null);

      try {
        const response = await fetch(
          `${API_URL}/forecast/day?delivery_date=${date}`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          let message = `API error ${response.status}`;

          try {
            const body = await response.json();
            if (typeof body.detail === "string") {
              message = body.detail;
            }
          } catch {
            // Keep the HTTP error message.
          }

          throw new Error(message);
        }

        const result: ForecastData = await response.json();
        if (!controller.signal.aborted) {
          setData(result);
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(
            err instanceof Error ? err.message : "Unable to load forecast"
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadForecast();

    return () => controller.abort();
  }, [date]);

  useEffect(() => {
    const controller = new AbortController();

    async function loadExplanation() {
      setMarketExplanation("");
      setExplanationError("");
      setExplanationLoading(true);

      try {
        const response = await fetch(
          `${API_URL}/forecast/day/explanation?delivery_date=${date}`,
          { signal: controller.signal }
        );
        if (!response.ok) {
          throw new Error(`Explanation API error ${response.status}`);
        }
        const result: ExplanationData = await response.json();
        if (!controller.signal.aborted && result.delivery_date === date) {
          setMarketExplanation(result.explanation);
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setExplanationError("Market insights are unavailable for this date.");
          console.error("Explanation request failed:", err);
        }
      } finally {
        if (!controller.signal.aborted) setExplanationLoading(false);
      }
    }

    loadExplanation();
    return () => controller.abort();
  }, [date]);

  const chartData = data?.hours.map((hour) => ({
    time: formatHour(hour.timestamp_local),
    price: hour.predicted_price_eur_mwh,
    load: hour.load_forecast_mw / 1000,
    wind: hour.wind_forecast_mw / 1000,
    solar: hour.solar_forecast_mw / 1000,
  }));

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/70">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-blue-600 p-3">
              <Zap size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold">EU Market Monitor</h1>
              <p className="text-sm text-slate-400">
                Electricity Market Forecasting & Intelligence
              </p>
            </div>
          </div>

          <span className="rounded-full border border-blue-800 bg-blue-950 px-4 py-2 text-sm text-blue-300">
            Historical Replay
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">
        <section className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold">
              Germany–Luxembourg Market
            </h2>
            <p className="mt-1 text-slate-400">
              XGBoost hourly price forecasts · Europe/Berlin time
            </p>
          </div>

          <label className="flex flex-col gap-2 text-sm text-slate-400">
            <span className="flex items-center gap-2">
              <CalendarDays size={16} />
              Delivery date
            </span>
            <input
              type="date"
              min="2023-01-03"
              max="2025-12-31"
              value={date}
              onChange={(event) => setDate(event.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-white"
            />
          </label>
        </section>

        <div className="rounded-lg border border-amber-900/60 bg-amber-950/30 p-4 text-sm text-amber-200">
          Historical replay analysis only. Original publication times of
          historical market forecasts have not been verified. Results should
          not be interpreted as leakage-safe live day-ahead performance.
        </div>

        {loading && (
          <p className="text-blue-300">Loading market forecast...</p>
        )}

        {error && (
          <div className="rounded-lg border border-red-800 bg-red-950/40 p-5 text-red-300">
            {error}
          </div>
        )}

        {data && !loading && (
          <>
            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {[
                {
                  label: "Average Price",
                  value: euro(data.summary.average_price),
                  icon: Activity,
                },
                {
                  label: "Maximum Price",
                  value: euro(data.summary.maximum_price),
                  icon: TrendingUp,
                },
                {
                  label: "Minimum Price",
                  value: euro(data.summary.minimum_price),
                  icon: TrendingDown,
                },
                {
                  label: "Price Spike Hours",
                  value: String(data.intelligence.spike_hours.length),
                  icon: AlertTriangle,
                },
              ].map((item) => {
                const Icon = item.icon;

                return (
                  <div
                    key={item.label}
                    className="rounded-xl border border-slate-800 bg-slate-900 p-6"
                  >
                    <div className="flex items-center justify-between text-slate-400">
                      <span className="text-sm">{item.label}</span>
                      <Icon size={20} />
                    </div>
                    <p className="mt-4 text-3xl font-bold">{item.value}</p>
                    <p className="mt-2 text-xs text-slate-500">
                      {item.label.includes("Hours")
                        ? "Predicted hours above €150/MWh"
                        : "EUR per MWh"}
                    </p>
                  </div>
                );
              })}
            </section>

            <section className="rounded-xl border border-slate-700 bg-slate-900 p-6" aria-live="polite">
              <div className="mb-3 flex items-center gap-3">
                <Lightbulb size={22} className="text-amber-300" aria-hidden="true" />
                <h3 className="text-xl font-semibold">Market Insights</h3>
              </div>
              {explanationLoading ? (
                <p className="text-slate-300">Analyzing this day's market patterns...</p>
              ) : explanationError ? (
                <p className="text-amber-200" role="status">{explanationError}</p>
              ) : (
                <p className="max-w-4xl text-base leading-7 text-slate-200">
                  {marketExplanation || "No market insights available."}
                </p>
              )}
              <p className="mt-4 text-xs text-slate-400">
                Evidence-based summary · Historical replay, not a live forecast
              </p>
            </section>

            <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-2 text-xl font-semibold">
                24-Hour Electricity Price Forecast
              </h3>
              <p className="mb-6 text-sm text-slate-400">
                Predicted day-ahead electricity prices (€/MWh)
              </p>

              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        border: "1px solid #334155",
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="price"
                      name="Predicted Price (€/MWh)"
                      stroke="#60a5fa"
                      strokeWidth={3}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                <h3 className="mb-6 text-xl font-semibold">
                  Market Fundamentals
                </h3>
                <p className="mb-4 text-sm text-slate-400">
                  Forecast load, wind and solar generation (GW)
                </p>

                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                      <XAxis dataKey="time" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#0f172a",
                          border: "1px solid #334155",
                        }}
                      />
                      <Legend />
                      <Line dataKey="load" stroke="#a78bfa" dot={false} />
                      <Line dataKey="wind" stroke="#34d399" dot={false} />
                      <Line dataKey="solar" stroke="#fbbf24" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                <h3 className="mb-6 text-xl font-semibold">
                  Forecast Intelligence
                </h3>

                <div className="space-y-4">
                  <div className="rounded-lg bg-slate-800 p-4">
                    <p className="text-sm text-slate-400">Cheapest Hour</p>
                    <p className="mt-2 text-xl font-semibold text-emerald-400">
                      {formatHour(
                        data.intelligence.cheapest_hour.timestamp_local
                      )}{" "}
                      · {euro(data.intelligence.cheapest_hour.price_eur_mwh)}
                    </p>
                  </div>

                  <div className="rounded-lg bg-slate-800 p-4">
                    <p className="text-sm text-slate-400">Most Expensive Hour</p>
                    <p className="mt-2 text-xl font-semibold text-rose-400">
                      {formatHour(
                        data.intelligence.most_expensive_hour.timestamp_local
                      )}{" "}
                      · {euro(
                        data.intelligence.most_expensive_hour.price_eur_mwh
                      )}
                    </p>
                  </div>

                  <div className="rounded-lg bg-slate-800 p-4">
                    <p className="text-sm text-slate-400">Daily Price Spread</p>
                    <p className="mt-2 text-xl font-semibold">
                      {euro(data.intelligence.daily_price_spread)}/MWh
                    </p>
                  </div>

                  <div className="rounded-lg bg-slate-800 p-4">
                    <p className="text-sm text-slate-400">
                      Predicted Negative-Price Hours
                    </p>
                    <p className="mt-2 text-xl font-semibold">
                      {data.intelligence.negative_price_hours.length}
                    </p>
                  </div>
                </div>
              </div>
            </section>

            <footer className="pb-6 text-center text-sm text-slate-500">
              EU Market Monitor · Historical forecast replay · XGBoost
            </footer>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
