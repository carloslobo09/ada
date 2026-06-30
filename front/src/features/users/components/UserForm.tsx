import { useEffect, useState, type ReactNode } from "react";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import type { Rol } from "@/features/auth/types";
import type {
  CreateUserInput,
  UpdateUserInput,
  Usuario,
} from "@/features/users/types";

interface UserFormProps {
  initial?: Usuario | null;
  submitting?: boolean;
  errorMessage?: string | null;
  onSubmitCreate?: (payload: CreateUserInput) => void;
  onSubmitUpdate?: (payload: UpdateUserInput) => void;
  onCancel?: () => void;
}

const ROL_OPTIONS: { value: Rol; label: string }[] = [
  { value: "cliente", label: "Cliente" },
  { value: "entrenador", label: "Entrenador" },
  { value: "admin", label: "Administrador" },
];

export function UserForm({
  initial,
  submitting = false,
  errorMessage,
  onSubmitCreate,
  onSubmitUpdate,
  onCancel,
}: UserFormProps): ReactNode {
  const isEdit = Boolean(initial);

  const [email, setEmail] = useState("");
  const [nombre, setNombre] = useState("");
  const [rol, setRol] = useState<Rol>("cliente");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    setEmail(initial?.email ?? "");
    setNombre(initial?.nombre ?? "");
    setRol(initial?.rol ?? "cliente");
    setPassword("");
    setFormError(null);
  }, [initial]);

  function handleSubmit(event: React.FormEvent): void {
    event.preventDefault();
    setFormError(null);

    if (!nombre.trim()) {
      setFormError("El nombre es obligatorio.");
      return;
    }

    if (isEdit && onSubmitUpdate) {
      onSubmitUpdate({ nombre: nombre.trim(), rol });
      return;
    }

    if (!email.trim()) {
      setFormError("El email es obligatorio.");
      return;
    }
    if (password.length < 6) {
      setFormError("La contrasena debe tener al menos 6 caracteres.");
      return;
    }
    onSubmitCreate?.({
      email: email.trim(),
      nombre: nombre.trim(),
      rol,
      password,
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-3 rounded-lg border border-slate-200 bg-white p-4"
    >
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block space-y-1">
          <span className="text-xs font-medium text-slate-700">Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isEdit}
            placeholder="usuario@dominio.com"
            className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 disabled:bg-slate-50 disabled:text-slate-500"
          />
        </label>

        <label className="block space-y-1">
          <span className="text-xs font-medium text-slate-700">Nombre</span>
          <input
            type="text"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="Nombre y apellido"
            className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </label>

        <label className="block space-y-1">
          <span className="text-xs font-medium text-slate-700">Rol</span>
          <select
            value={rol}
            onChange={(e) => setRol(e.target.value as Rol)}
            className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          >
            {ROL_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </label>

        {!isEdit && (
          <label className="block space-y-1">
            <span className="text-xs font-medium text-slate-700">Contrasena inicial</span>
            <input
              type="text"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Minimo 6 caracteres"
              className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </label>
        )}
      </div>

      {formError && <Alert variant="danger">{formError}</Alert>}
      {errorMessage && (
        <Alert variant="danger" title="No se pudo guardar">
          {errorMessage}
        </Alert>
      )}

      <div className="flex justify-end gap-2">
        {onCancel && (
          <Button type="button" variant="secondary" size="sm" onClick={onCancel}>
            Cancelar
          </Button>
        )}
        <Button type="submit" size="sm" loading={submitting}>
          {isEdit ? "Guardar cambios" : "Crear usuario"}
        </Button>
      </div>
    </form>
  );
}
