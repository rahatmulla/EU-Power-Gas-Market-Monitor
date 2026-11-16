import type { ForecastData } from "../types/market";
import { euro, formatHour } from "../types/market";

export default function IntelligencePanel({ data }: { data: ForecastData }) {
  const items = [
    { label: "Cheapest Hour", value: `${formatHour(data.intelligence.cheapest_hour.timestamp_local)} · ${euro(data.intelligence.cheapest_hour.price_eur_mwh)}`, tone: "text-emerald-300" },
    { label: "Most Expensive Hour", value: `${formatHour(data.intelligence.most_expensive_hour.timestamp_local)} · ${euro(data.intelligence.most_expensive_hour.price_eur_mwh)}`, tone: "text-orange-300" },
    { label: "Daily Price Spread", value: `${euro(data.intelligence.daily_price_spread)}/MWh`, tone: "text-stone-50" },
    { label: "Predicted Negative-Price Hours", value: String(data.intelligence.negative_price_hours.length), tone: "text-stone-50" },
  ];
  return (
    <section className="rounded-2xl border border-stone-800 bg-stone-900 p-5 md:p-6">
      <h3 className="mb-5 text-lg font-semibold text-stone-50">Forecast Intelligence</h3>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
        {items.map(({ label, value, tone }) => (
          <div key={label} className="rounded-xl border border-stone-800 bg-stone-950/70 p-4">
            <p className="text-sm text-stone-400">{label}</p>
            <p className={`mt-2 text-lg font-semibold ${tone}`}>{value}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
