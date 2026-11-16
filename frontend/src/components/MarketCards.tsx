import { Activity, AlertTriangle, TrendingDown, TrendingUp } from "lucide-react";
import type { ForecastData } from "../types/market";
import { euro } from "../types/market";

export default function MarketCards({ data }: { data: ForecastData }) {
  const cards = [
    { label: "Average Price", value: euro(data.summary.average_price), icon: Activity },
    { label: "Maximum Price", value: euro(data.summary.maximum_price), icon: TrendingUp },
    { label: "Minimum Price", value: euro(data.summary.minimum_price), icon: TrendingDown },
    { label: "Price Spike Hours", value: String(data.intelligence.spike_hours.length), icon: AlertTriangle },
  ];
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" aria-label="Forecast summary">
      {cards.map(({ label, value, icon: Icon }) => (
        <article key={label} className="rounded-2xl border border-stone-800 bg-stone-900 p-5 shadow-lg shadow-black/10">
          <div className="flex items-center justify-between text-stone-400">
            <span className="text-sm">{label}</span><Icon size={19} className="text-amber-500" />
          </div>
          <p className="mt-5 text-3xl font-semibold tracking-tight text-stone-50">{value}</p>
          <p className="mt-2 text-xs text-stone-500">{label.includes("Hours") ? "Predicted hours above €150/MWh" : "EUR per MWh"}</p>
        </article>
      ))}
    </section>
  );
}
