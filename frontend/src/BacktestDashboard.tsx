
import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type BacktestHour = {
  timestamp_utc: string;
  delivery_date: string;
  actual: number;
  predicted: number;
  baseline: number;
};

type BacktestResponse = {
  forecast_type: string;
  publication_vintage_verified: boolean;
  summary: {
    days_evaluated: number;
    hours_evaluated: number;
    model_mae: number;
    baseline_mae: number;
    improvement_percent: number | null;
  };
  monthly: {
    month: string;
    hours: number;
    model_mae: number;
    baseline_mae: number;
  }[];
  hourly: BacktestHour[];
};

const API_URL = "http://localhost:8000";

export default function BacktestDashboard() {
  const [data, setData] = useState<BacktestResponse | null>(null);
  const [selectedDate, setSelectedDate] = useState("2025-07-15");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      try {
        const response = await fetch(`${API_URL}/forecast/backtest`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Backtest API error: ${response.status}`);
        }

        const result: BacktestResponse = await response.json();
        if (!controller.signal.aborted) setData(result);
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : "Unable to load");
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    load();
    return () => controller.abort();
  }, []);

  const dailyData = useMemo(() => {
    if (!data) return [];

    return data.hourly
      .filter((row) => row.delivery_date === selectedDate)
      .map((row) => ({
        ...row,
        time: new Date(row.timestamp_utc).toLocaleTimeString("en-GB", {
          timeZone: "Europe/Berlin",
          hour: "2-digit",
          minute: "2-digit",
        }),
      }));
  }, [data, selectedDate]);

  if (loading) {
    return <p className="text-blue-300">Loading backtest results...</p>;
  }

  if (error || !data) {
    return <p className="text-red-300">{error || "No results available"}</p>;
  }

  const summary = data.summary;

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">
          Accuracy & Backtesting
        </h2>
        <p className="mt-1 text-sm text-slate-400">
          2025 historical electricity price prediction performance
        </p>
      </div>

      <div className="rounded-lg border border-amber-900/60 bg-amber-950/30 p-4 text-sm text-amber-200">
        Historical replay only. Original market forecast publication
        times have not been verified, so these scores are not confirmed
        leakage-free day-ahead performance.
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ["XGBoost MAE", `€${summary.model_mae.toFixed(2)}/MWh`],
          ["Baseline MAE", `€${summary.baseline_mae.toFixed(2)}/MWh`],
          [
            "MAE Improvement",
            summary.improvement_percent === null
              ? "N/A"
              : `${summary.improvement_percent.toFixed(1)}%`,
          ],
          ["Hours Evaluated", summary.hours_evaluated.toLocaleString()],
        ].map(([label, value]) => (
          <div
            key={label}
            className="rounded-xl border border-slate-800 bg-slate-900 p-5"
          >
            <p className="text-sm text-slate-400">{label}</p>
            <p className="mt-3 text-2xl font-bold">{value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="mb-2 text-xl font-semibold">
          Monthly Forecasting Error
        </h3>
        <p className="mb-5 text-sm text-slate-400">
          Average absolute error in €/MWh. Lower is better.
        </p>

        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.monthly}>
              <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
              <XAxis dataKey="month" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  border: "1px solid #334155",
                }}
              />
              <Legend />
              <Line
                dataKey="model_mae"
                name="XGBoost MAE"
                stroke="#34d399"
                strokeWidth={3}
              />
              <Line
                dataKey="baseline_mae"
                name="Baseline MAE"
                stroke="#fbbf24"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-semibold">
              Actual vs Predicted Prices
            </h3>
            <p className="mt-1 text-sm text-slate-400">
              Hourly prices in €/MWh · German local time
            </p>
          </div>

          <label className="flex flex-col gap-2 text-sm text-slate-400">
            Select delivery date
            <input
              type="date"
              min="2025-01-03"
              max="2025-12-31"
              value={selectedDate}
              onChange={(event) => setSelectedDate(event.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white"
            />
          </label>
        </div>

        {dailyData.length === 0 ? (
          <p className="text-amber-300">
            No backtest results available for this date.
          </p>
        ) : (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dailyData}>
                <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                <XAxis
                  dataKey="time"
                  stroke="#94a3b8"
                  interval="preserveStartEnd"
                />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    border: "1px solid #334155",
                  }}
                />
                <Legend />
                <Line
                  dataKey="actual"
                  name="Actual Price"
                  stroke="#34d399"
                  strokeWidth={3}
                  dot={false}
                />
                <Line
                  dataKey="predicted"
                  name="XGBoost Prediction"
                  stroke="#60a5fa"
                  strokeWidth={3}
                  dot={false}
                />
                <Line
                  dataKey="baseline"
                  name="Baseline"
                  stroke="#fbbf24"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <p className="text-xs text-slate-500">
        {summary.days_evaluated} delivery days evaluated. DST-adjusted
        baseline and estimated missing forecast values are included.
      </p>
    </section>
  );
}
