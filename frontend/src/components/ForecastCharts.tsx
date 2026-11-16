import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { ChartHour } from "../types/market";

const grid = "#44403c";
const axis = "#a8a29e";
const tooltipStyle = { backgroundColor: "#292524", border: "1px solid #57534e", borderRadius: 12, color: "#fafaf9" };

export function PriceForecastChart({ data }: { data: ChartHour[] }) {
  return (
    <section className="rounded-2xl border border-stone-800 bg-stone-900 p-5 md:p-6">
      <h3 className="text-lg font-semibold text-stone-50">Electricity Price Forecast</h3>
      <p className="mt-1 mb-6 text-sm text-stone-400">Predicted day-ahead electricity prices (€/MWh) · Europe/Berlin</p>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="time" stroke={axis} tick={{ fontSize: 11 }} interval="preserveStartEnd" />
            <YAxis stroke={axis} tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
            <Line type="monotone" dataKey="price" name="Predicted Price (€/MWh)" stroke="#f59e0b" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export function FundamentalsChart({ data }: { data: ChartHour[] }) {
  return (
    <section className="rounded-2xl border border-stone-800 bg-stone-900 p-5 md:p-6">
      <h3 className="text-lg font-semibold text-stone-50">Market Fundamentals</h3>
      <p className="mt-1 mb-5 text-sm text-stone-400">Forecast load, wind and solar generation (GW)</p>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="time" stroke={axis} tick={{ fontSize: 11 }} interval="preserveStartEnd" />
            <YAxis stroke={axis} tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
            <Line dataKey="load" stroke="#f97316" dot={false} strokeWidth={2} />
            <Line dataKey="wind" stroke="#86efac" dot={false} strokeWidth={2} />
            <Line dataKey="solar" stroke="#fcd34d" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
