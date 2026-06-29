import type { ReactNode } from "react";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
}

const SIZES = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-10 w-10",
} as const;

export function Spinner({ size = "md" }: SpinnerProps): ReactNode {
  return (
    <span
      className={`inline-block animate-spin rounded-full border-2 border-current border-t-transparent ${SIZES[size]}`}
      role="status"
      aria-label="Cargando"
    />
  );
}
