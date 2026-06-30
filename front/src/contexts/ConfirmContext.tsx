import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { ConfirmDialog, type ConfirmOptions } from "@/components/ConfirmDialog";

type ConfirmFn = (options: ConfirmOptions) => Promise<boolean>;

const ConfirmContext = createContext<ConfirmFn | undefined>(undefined);

interface ConfirmProviderProps {
  children: ReactNode;
}

export function ConfirmProvider({ children }: ConfirmProviderProps): ReactNode {
  const [state, setState] = useState<{
    options: ConfirmOptions;
    open: boolean;
  } | null>(null);
  const resolverRef = useRef<((value: boolean) => void) | null>(null);

  const confirm: ConfirmFn = useCallback((options) => {
    return new Promise<boolean>((resolve) => {
      resolverRef.current = resolve;
      setState({ options, open: true });
    });
  }, []);

  function settle(value: boolean): void {
    resolverRef.current?.(value);
    resolverRef.current = null;
    setState((prev) => (prev ? { ...prev, open: false } : null));
  }

  return (
    <ConfirmContext.Provider value={confirm}>
      {children}
      {state && (
        <ConfirmDialog
          open={state.open}
          title={state.options.title}
          message={state.options.message}
          confirmLabel={state.options.confirmLabel}
          cancelLabel={state.options.cancelLabel}
          variant={state.options.variant}
          onConfirm={() => settle(true)}
          onCancel={() => settle(false)}
        />
      )}
    </ConfirmContext.Provider>
  );
}

export function useConfirm(): ConfirmFn {
  const ctx = useContext(ConfirmContext);
  if (!ctx) {
    throw new Error("useConfirm debe usarse dentro de un ConfirmProvider.");
  }
  return ctx;
}
