import { Lightbulb } from "lucide-react";

type Props = { explanation: string; loading: boolean; error: string };
export default function ExplanationPanel({ explanation, loading, error }: Props) {
  return (
    <aside className="rounded-2xl border border-amber-900/40 bg-stone-900 p-5 md:p-6" aria-live="polite">
      <div className="mb-4 flex items-center gap-3">
        <div className="rounded-lg bg-amber-500/10 p-2"><Lightbulb size={20} className="text-amber-400" aria-hidden="true" /></div>
        <h3 className="text-lg font-semibold text-stone-50">AI Market Explanation</h3>
      </div>
      {loading ? (
        <p className="text-stone-300">Analyzing this day's market patterns...</p>
      ) : error ? (
        <p className="text-amber-200" role="status">{error}</p>
      ) : (
        <p className="whitespace-pre-line text-sm leading-7 text-stone-200">{explanation || "No market insights available."}</p>
      )}
      <p className="mt-6 border-t border-stone-800 pt-4 text-xs leading-5 text-stone-500">
        Evidence-based summary · Historical replay, not a live forecast
      </p>
    </aside>
  );
}
