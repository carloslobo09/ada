import { useEffect, useState, type ReactNode } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import { Spinner } from "@/components/Spinner";
import { CrossFieldsEditor } from "@/features/prompts/components/CrossFieldsEditor";
import { useCreatePromptVersion } from "@/features/prompts/hooks/useCreatePromptVersion";
import { useGetPromptVersion } from "@/features/prompts/hooks/useGetPromptVersion";
import { useListPromptVersions } from "@/features/prompts/hooks/useListPromptVersions";
import type { CrossFieldConfig } from "@/features/prompts/types";
import { extractApiMessage } from "@/lib/errors";

export function CreatePromptVersionPage(): ReactNode {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const baseId = params.get("base");
  const base = useGetPromptVersion(baseId ?? undefined);
  const list = useListPromptVersions();

  const [promptText, setPromptText] = useState("");
  const [crossFields, setCrossFields] = useState<CrossFieldConfig[]>([]);
  const [tipoDocumentoId, setTipoDocumentoId] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (base.data) {
      setPromptText(base.data.prompt_text);
      setCrossFields(base.data.cross_validation_config);
      setTipoDocumentoId(base.data.tipo_documento_id);
    }
  }, [base.data]);

  useEffect(() => {
    if (baseId || tipoDocumentoId !== null) return;
    const first = list.data?.[0];
    if (first) {
      setTipoDocumentoId(first.tipo_documento_id);
    }
  }, [baseId, tipoDocumentoId, list.data]);

  const mutation = useCreatePromptVersion();

  function onSubmit(event: React.FormEvent): void {
    event.preventDefault();
    setFormError(null);

    if (!tipoDocumentoId) {
      setFormError("No se pudo determinar el tipo documental destino.");
      return;
    }
    if (!promptText.trim()) {
      setFormError("El prompt no puede estar vacio.");
      return;
    }
    if (crossFields.some((f) => !f.field.trim())) {
      setFormError("Todos los campos de validacion cruzada deben tener un nombre.");
      return;
    }

    mutation.mutate(
      {
        tipo_documento_id: tipoDocumentoId,
        prompt_text: promptText,
        cross_validation_config: crossFields,
      },
      {
        onSuccess: (version) => {
          navigate(`/configuracion/${version.id}`);
        },
      },
    );
  }

  if (baseId && base.isLoading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-500">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <form className="space-y-6" onSubmit={onSubmit}>
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-900">Nueva version</h1>
        <p className="text-sm text-slate-600">
          {baseId
            ? "Edita una copia de la version seleccionada. Se crea como borrador y se publica desde el detalle."
            : "Carga el prompt y la configuracion de validacion cruzada. Se crea como borrador y se publica desde el detalle."}
        </p>
      </header>

      <section className="space-y-3 rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">Prompt</h2>
        <textarea
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)}
          rows={18}
          className="w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-xs focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
      </section>

      <section className="space-y-3 rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
          Validacion cruzada
        </h2>
        <CrossFieldsEditor value={crossFields} onChange={setCrossFields} />
      </section>

      {formError && <Alert variant="danger">{formError}</Alert>}
      {mutation.error && (
        <Alert variant="danger" title="No se pudo crear la version">
          {extractApiMessage(mutation.error)}
        </Alert>
      )}

      <div className="flex justify-end gap-2">
        <Button
          type="button"
          variant="secondary"
          onClick={() => navigate("/configuracion")}
        >
          Cancelar
        </Button>
        <Button type="submit" loading={mutation.isPending}>
          Crear version
        </Button>
      </div>
    </form>
  );
}
