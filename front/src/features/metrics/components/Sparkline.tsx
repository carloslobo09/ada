import type { ReactNode } from "react";
import type { CasosPorDia } from "@/features/metrics/types";

interface SparklineProps {
  serie: CasosPorDia[];
}

export function Sparkline({ serie }: SparklineProps): ReactNode {
  if (serie.length === 0) {
    return <p className="text-xs text-slate-500">Sin datos.</p>;
  }

  const max = Math.max(1, ...serie.map((d) => d.cantidad));

  return (
    <div className="flex items-end gap-0.5 h-24">
      {serie.map((d) => {
        const heightPct = (d.cantidad / max) * 100;
        return (
          <div
            key={d.fecha}
            className="group relative h-full flex-1 min-w-[3px]"
            title={`${d.fecha}: ${d.cantidad} casos`}
          >
            <div
              className="absolute bottom-0 left-0 right-0 rounded-t bg-brand-400 transition-colors group-hover:bg-brand-600"
              style={{ height: `${heightPct}%`, minHeight: d.cantidad > 0 ? "2px" : "0" }}
            />
          </div>
        );
      })}
    </div>
  );
}
