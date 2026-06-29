import type { ReactNode } from "react";
import type { Veredicto } from "@/features/cases/types";

interface DecisionBadgeProps {
  veredicto: Veredicto | null;
}

const STYLES: Record<Veredicto, string> = {
  approved: "bg-emerald-100 text-emerald-800 border-emerald-200",
  rejected: "bg-rose-100 text-rose-800 border-rose-200",
};

const LABELS: Record<Veredicto, string> = {
  approved: "Aprobado",
  rejected: "Rechazado",
};

export function DecisionBadge({ veredicto }: DecisionBadgeProps): ReactNode {
  if (!veredicto) {
    return (
      <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700">
        Pendiente
      </span>
    );
  }
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide ${STYLES[veredicto]}`}
    >
      {LABELS[veredicto]}
    </span>
  );
}
