import type { ReactNode } from "react";
import type { RuleResult } from "@/features/cases/types";

interface RuleResultsListProps {
  results: RuleResult[];
}

export function RuleResultsList({ results }: RuleResultsListProps): ReactNode {
  if (results.length === 0) {
    return <p className="text-sm text-slate-500">Sin reglas evaluadas.</p>;
  }
  return (
    <ul className="divide-y divide-slate-100 rounded-md border border-slate-200 bg-white">
      {results.map((result) => (
        <li key={result.name} className="flex items-start justify-between gap-3 px-4 py-3">
          <div className="space-y-0.5">
            <p className="text-sm font-medium text-slate-900">{result.name}</p>
            <p className="text-xs text-slate-500">
              {result.severity === "critical" ? "Critica" : "Informativa"} - {result.reason}
            </p>
          </div>
          <ResultPill passed={result.passed} />
        </li>
      ))}
    </ul>
  );
}

function ResultPill({ passed }: { passed: boolean }): ReactNode {
  return (
    <span
      className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide ${
        passed ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
      }`}
    >
      {passed ? "Aprobado" : "Rechazado"}
    </span>
  );
}
