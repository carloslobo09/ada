import type { ReactNode } from "react";
import { humanize } from "@/lib/strings";

interface NormalizedFieldsTableProps {
  data: Record<string, unknown>;
  labels?: Record<string, string>;
}

export function NormalizedFieldsTable({
  data,
  labels,
}: NormalizedFieldsTableProps): ReactNode {
  const keys = Object.keys(data);
  if (keys.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        El modelo no devolvio campos extraidos.
      </p>
    );
  }

  return (
    <dl className="grid gap-y-3 gap-x-6 rounded-md border border-slate-200 bg-white p-4 sm:grid-cols-2">
      {keys.map((key) => (
        <div key={key} className="flex flex-col">
          <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
            {labels?.[key] ?? humanize(key)}
          </dt>
          <dd className="text-sm text-slate-900">{formatValue(data[key])}</dd>
        </div>
      ))}
    </dl>
  );
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "boolean") return value ? "Si" : "No";
  return String(value);
}
