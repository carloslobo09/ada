import type { ReactNode } from "react";

type Variant = "info" | "success" | "warning" | "danger";

interface AlertProps {
  variant?: Variant;
  title?: string;
  children: ReactNode;
}

const STYLES: Record<Variant, string> = {
  info: "border-brand-200 bg-brand-50 text-brand-900",
  success: "border-emerald-200 bg-emerald-50 text-emerald-900",
  warning: "border-amber-200 bg-amber-50 text-amber-900",
  danger: "border-rose-200 bg-rose-50 text-rose-900",
};

export function Alert({ variant = "info", title, children }: AlertProps): ReactNode {
  return (
    <div className={`rounded-md border px-4 py-3 ${STYLES[variant]}`} role="status">
      {title && <p className="text-sm font-semibold">{title}</p>}
      <div className="text-sm">{children}</div>
    </div>
  );
}
