import type { ReactNode } from "react";
import type { EstadoRecontrol } from "@/features/cases/types";

interface RecontrolBadgeProps {
  estado: EstadoRecontrol;
  size?: "sm" | "md";
}

const STYLES: Record<EstadoRecontrol, string> = {
  pendiente: "bg-slate-100 text-slate-700 border-slate-200",
  correcto: "bg-sky-100 text-sky-800 border-sky-200",
  incorrecto: "bg-amber-100 text-amber-800 border-amber-200",
};

const LABELS: Record<EstadoRecontrol, string> = {
  pendiente: "Sin revisar",
  correcto: "Re Control OK",
  incorrecto: "Re Control con observacion",
};

export function RecontrolBadge({ estado, size = "sm" }: RecontrolBadgeProps): ReactNode {
  const padding = size === "sm" ? "px-2 py-0.5" : "px-2.5 py-1";
  return (
    <span
      className={`inline-flex items-center rounded-full border ${padding} text-xs font-medium ${STYLES[estado]}`}
    >
      {LABELS[estado]}
    </span>
  );
}
