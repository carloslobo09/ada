import type { ReactNode } from "react";

interface HorizontalBarProps {
  label: string;
  value: number;
  total: number;
  color: "emerald" | "rose" | "slate" | "amber";
}

const COLOR_BG: Record<HorizontalBarProps["color"], string> = {
  emerald: "bg-emerald-500",
  rose: "bg-rose-500",
  slate: "bg-slate-400",
  amber: "bg-amber-500",
};

export function HorizontalBar({
  label,
  value,
  total,
  color,
}: HorizontalBarProps): ReactNode {
  const pct = total > 0 ? Math.round((value / total) * 1000) / 10 : 0;
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between text-xs">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="text-slate-500">
          {value} <span className="text-slate-400">({pct.toFixed(1)}%)</span>
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full ${COLOR_BG[color]} transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
