import type { ReactNode } from "react";
import type { EstadoPromptVersion } from "@/features/prompts/types";

interface EstadoBadgeProps {
  estado: EstadoPromptVersion;
}

const STYLES: Record<EstadoPromptVersion, { label: string; classes: string }> = {
  publicada: {
    label: "Publicada",
    classes:
      "border-emerald-200 bg-emerald-100 text-emerald-800 font-semibold",
  },
  borrador: {
    label: "Borrador",
    classes: "border-amber-200 bg-amber-100 text-amber-800 font-medium",
  },
  archivada: {
    label: "Archivada",
    classes: "border-slate-200 bg-slate-100 text-slate-600 font-medium",
  },
};

export function ActiveBadge({ estado }: EstadoBadgeProps): ReactNode {
  const { label, classes } = STYLES[estado];
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs uppercase tracking-wide ${classes}`}
    >
      {label}
    </span>
  );
}
