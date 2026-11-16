
import { useEffect, useState } from "react";
import {
  CalendarDays,
  ChartNoAxesCombined,
  Zap,
  ChartColumnIncreasing,
} from "lucide-react";

import MarketCards from "./components/MarketCards";
import {
  FundamentalsChart,
  PriceForecastChart,
} from "./components/ForecastCharts";
import IntelligencePanel from "./components/IntelligencePanel";
import ExplanationPanel from "./components/ExplanationPanel";
import BacktestDashboard from "./BacktestDashboard";

import type { ForecastData, ExplanationData } from "./types/market";
import { formatHour } from "./types/market";

const API_URL = "http://localhost:8000";

type DashboardTab = "forecast" | "backtest";

function App() {
  const [activeTab, setActiveTab] = useState<DashboardTab>("forecast");

  const [date, setDate] = useState("2025-07-15");
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [marketExplanation, setMarketExplanation] = useState("");
  const [explanationLoading, setExplanationLoading] = useState(false);
  const [explanationError, setExplanationError] = useState("");

  // Load electricity price forecast
  useEffect(() => {
    if (activeTab !== "forecast") return;

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
            err instanceof Error
              ? err.message
              : "Unable to load forecast"
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
  }, [date, activeTab]);

  // Load market explanation
  useEffect(() => {
    if (activeTab !== "forecast") return;

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

        if (
          !controller.signal.aborted &&
          result.delivery_date === date
        ) {
          setMarketExplanation(result.explanation);
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setExplanationError(
            "Market insights are unavailable for this date."
          );
          console.error("Explanation request failed:", err);
        }
      } finally {
        if (!controller.signal.aborted) {
          setExplanationLoading(false);
        }
      }
    }

    loadExplanation();

    return () => controller.abort();
  }, [date, activeTab]);

  const chartData = data?.hours.map((hour) => ({
    time: formatHour(hour.timestamp_local),
    price: hour.predicted_price_eur_mwh,
    load: hour.load_forecast_mw / 1000,
    wind: hour.wind_forecast_mw / 1000,
    solar: hour.solar_forecast_mw / 1000,
  }));

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100">
      {/* Header */}
      <header className="border-b border-stone-800 bg-stone-900/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-5 md:px-8">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-amber-500 p-3 text-stone-950">
              <Zap size={23} />
            </div>

            <div>
              <h1 className="text-xl font-bold tracking-tight md:text-2xl">
                EU Market Monitor
              </h1>
              <p className="text-xs text-stone-400 md:text-sm">
                Electricity Market Forecasting & Intelligence
              </p>
            </div>
          </div>

          <span className="rounded-full border border-amber-800/60 bg-amber-500/10 px-3 py-2 text-xs font-medium text-amber-300 md:text-sm">
            Historical Replay
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-5 py-8 md:px-8">
        {/* Navigation */}
        <nav
          className="flex flex-wrap gap-3 border-b border-stone-800 pb-5"
          aria-label="Dashboard navigation"
        >
          <button
            type="button"
            onClick={() => setActiveTab("forecast")}
            aria-pressed={activeTab === "forecast"}
            className={`flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold transition ${
              activeTab === "forecast"
                ? "bg-amber-500 text-stone-950"
                : "border border-stone-700 bg-stone-900 text-stone-300 hover:border-amber-500 hover:text-amber-300"
            }`}
          >
            <ChartNoAxesCombined size={18} />
            Forecast Dashboard
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("backtest")}
            aria-pressed={activeTab === "backtest"}
            className={`flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold transition ${
              activeTab === "backtest"
                ? "bg-amber-500 text-stone-950"
                : "border border-stone-700 bg-stone-900 text-stone-300 hover:border-amber-500 hover:text-amber-300"
            }`}
          >
            <ChartColumnIncreasing size={18} />
            Accuracy & Backtesting
          </button>
        </nav>

        {/* Forecast Dashboard */}
        {activeTab === "forecast" && (
          <>
            <div className="flex flex-wrap items-end justify-between gap-5">
              <div>
                <p className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-amber-400">
                  <ChartNoAxesCombined size={15} />
                  Forecast Dashboard
                </p>

                <h2 className="text-2xl font-semibold tracking-tight md:text-3xl">
                  Germany–Luxembourg Market
                </h2>

                <p className="mt-2 text-sm text-stone-400">
                  XGBoost hourly price forecasts · Europe/Berlin time
                </p>
              </div>

              <label className="flex flex-col gap-2 text-sm text-stone-300">
                <span className="flex items-center gap-2">
                  <CalendarDays
                    size={16}
                    className="text-amber-400"
                  />
                  Delivery date
                </span>

                <input
                  type="date"
                  min="2023-01-03"
                  max="2025-12-31"
                  value={date}
                  onChange={(event) => setDate(event.target.value)}
                  className="rounded-xl border border-stone-700 bg-stone-900 px-4 py-3 text-stone-50 outline-none focus:border-amber-500"
                />
              </label>
            </div>

            <div className="rounded-xl border border-amber-900/50 bg-amber-500/10 px-5 py-4 text-sm leading-6 text-amber-200">
              Historical replay analysis only. Original publication
              times of historical market forecasts have not been
              verified. Results should not be interpreted as
              leakage-safe live day-ahead performance.
            </div>

            {loading && (
              <p className="text-amber-300" role="status">
                Loading market forecast...
              </p>
            )}

            {error && (
              <div
                className="rounded-xl border border-red-900 bg-red-950/40 p-5 text-red-300"
                role="alert"
              >
                {error}
              </div>
            )}

            {data && !loading && chartData && (
              <>
                <MarketCards data={data} />

                <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1.8fr)_minmax(300px,1fr)]">
                  <PriceForecastChart data={chartData} />

                  <ExplanationPanel
                    explanation={marketExplanation}
                    loading={explanationLoading}
                    error={explanationError}
                  />
                </div>

                <div className="grid items-start gap-5 lg:grid-cols-2">
                  <FundamentalsChart data={chartData} />
                  <IntelligencePanel data={data} />
                </div>

                <footer className="pb-5 pt-3 text-center text-xs text-stone-500">
                  EU Market Monitor · Historical forecast replay · XGBoost
                </footer>
              </>
            )}
          </>
        )}

        {/* Accuracy & Backtesting Dashboard */}
        {activeTab === "backtest" && <BacktestDashboard />}
      </main>
    </div>
  );
}

export default App;
