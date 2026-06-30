import { useEffect, useState, type ReactNode } from "react";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import type {
  CreateTipoDocumentoInput,
  TipoDocumento,
} from "@/features/document-types/types";

interface TipoDocumentoFormProps {
  initial?: TipoDocumento | null;
  submitting?: boolean;
  errorMessage?: string | null;
  onSubmit: (payload: CreateTipoDocumentoInput) => void;
  onCancel?: () => void;
  submitLabel?: string;
}

export function TipoDocumentoForm({
  initial,
  submitting = false,
  errorMessage,
  onSubmit,
  onCancel,
  submitLabel = "Guardar",
}: TipoDocumentoFormProps): ReactNode {
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    setNombre(initial?.nombre ?? "");
    setDescripcion(initial?.descripcion ?? "");
    setFormError(null);
  }, [initial]);

  function handleSubmit(event: React.FormEvent): void {
    event.preventDefault();
    setFormError(null);
    if (!nombre.trim()) {
      setFormError("El nombre es obligatorio.");
      return;
    }
    onSubmit({
      nombre: nombre.trim(),
      descripcion: descripcion.trim() ? descripcion.trim() : null,
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-3 rounded-lg border border-slate-200 bg-white p-4"
    >
      <label className="block space-y-1">
        <span className="text-xs font-medium text-slate-700">Nombre</span>
        <input
          type="text"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          placeholder="DNI Argentino"
          className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
      </label>

      <label className="block space-y-1">
        <span className="text-xs font-medium text-slate-700">Descripcion</span>
        <textarea
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
          rows={3}
          placeholder="Documento Nacional de Identidad emitido por el Registro Nacional de las Personas."
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
      </label>

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
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}
