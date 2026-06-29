import type { ReactNode } from "react";
import type { CrossValidationResult } from "@/features/cases/types";

interface CrossValidationListProps {
  results: CrossValidationResult[];
}

export function CrossValidationList({ results }: CrossValidationListProps): ReactNode {
  if (results.length === 0) {
    return <p className="text-sm text-slate-500">No se ejecutaron comparaciones cruzadas.</p>;
  }
  return (
    <div className="overflow-x-auto rounded-md border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-2 text-left font-semibold">Campo</th>
            <th className="px-4 py-2 text-left font-semibold">Esperado</th>
            <th className="px-4 py-2 text-left font-semibold">Extraido</th>
            <th className="px-4 py-2 text-left font-semibold">Comparador</th>
            <th className="px-4 py-2 text-left font-semibold">Resultado</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {results.map((result) => (
            <tr key={result.field}>
              <td className="px-4 py-2 font-medium text-slate-900">
                {result.field}
                {result.critical && <span className="ml-1 text-xs text-rose-600">*</span>}
              </td>
              <td className="px-4 py-2 text-slate-700">{result.expected}</td>
              <td className="px-4 py-2 text-slate-700">{result.extracted || "-"}</td>
              <td className="px-4 py-2 text-slate-500">{result.comparison}</td>
              <td className="px-4 py-2">
                <span
                  className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide ${
                    result.passed
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-rose-100 text-rose-800"
                  }`}
                  title={result.reason}
                >
                  {result.passed ? "Aprobado" : "Rechazado"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="border-t border-slate-200 bg-slate-50 px-4 py-2 text-xs text-slate-500">
        * Campos criticos: un fallo lleva la decision a rechazado.
      </p>
    </div>
  );
}
