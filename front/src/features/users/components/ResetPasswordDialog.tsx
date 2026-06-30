import { useEffect, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";

interface ResetPasswordDialogProps {
  open: boolean;
  usuarioNombre: string;
  submitting?: boolean;
  errorMessage?: string | null;
  onConfirm: (newPassword: string) => void;
  onCancel: () => void;
}

export function ResetPasswordDialog({
  open,
  usuarioNombre,
  submitting = false,
  errorMessage,
  onConfirm,
  onCancel,
}: ResetPasswordDialogProps): ReactNode {
  const [newPassword, setNewPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setNewPassword("");
      setFormError(null);
    }
  }, [open]);

  if (!open) return null;

  function handleSubmit(event: React.FormEvent): void {
    event.preventDefault();
    if (newPassword.length < 6) {
      setFormError("La contrasena debe tener al menos 6 caracteres.");
      return;
    }
    onConfirm(newPassword);
  }

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4"
      role="dialog"
      aria-modal="true"
      onClick={(event) => {
        if (event.target === event.currentTarget) onCancel();
      }}
    >
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 rounded-xl bg-white p-6 shadow-xl"
      >
        <header className="space-y-1">
          <h2 className="text-base font-semibold text-slate-900">
            Resetear contrasena
          </h2>
          <p className="text-sm text-slate-600">
            Vas a asignarle una nueva contrasena a{" "}
            <span className="font-medium">{usuarioNombre}</span>. La actual va a dejar de
            funcionar inmediatamente.
          </p>
        </header>

        <label className="block space-y-1">
          <span className="text-xs font-medium text-slate-700">Nueva contrasena</span>
          <input
            type="text"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Minimo 6 caracteres"
            autoFocus
            className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </label>

        {formError && <Alert variant="danger">{formError}</Alert>}
        {errorMessage && (
          <Alert variant="danger" title="No se pudo resetear">
            {errorMessage}
          </Alert>
        )}

        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" size="sm" onClick={onCancel}>
            Cancelar
          </Button>
          <Button type="submit" size="sm" loading={submitting}>
            Resetear
          </Button>
        </div>
      </form>
    </div>,
    document.body,
  );
}
