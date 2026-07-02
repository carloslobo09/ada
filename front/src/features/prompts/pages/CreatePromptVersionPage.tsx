import { useEffect, useState, type ReactNode } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import { Spinner } from "@/components/Spinner";
import { useGetTipoDocumento } from "@/features/document-types/hooks/useGetTipoDocumento";
import { CrossFieldsEditor } from "@/features/prompts/components/CrossFieldsEditor";
import { ExtractionFieldsEditor } from "@/features/prompts/components/ExtractionFieldsEditor";
import { useCreatePromptVersion } from "@/features/prompts/hooks/useCreatePromptVersion";
import { useGetPromptVersion } from "@/features/prompts/hooks/useGetPromptVersion";
import type { CrossFieldConfig, ExtractionField } from "@/features/prompts/types";
import { extractApiMessage } from "@/lib/errors";

export function CreatePromptVersionPage(): ReactNode {
  const navigate = useNavigate();
  const { tipoId } = useParams<{ tipoId: string }>();
  const [params] = useSearchParams();
  const baseId = params.get("base");

  const tipo = useGetTipoDocumento(tipoId);
  const base = useGetPromptVersion(baseId ?? undefined);

  const [promptText, setPromptText] = useState("");
  const [extractionFields, setExtractionFields] = useState<ExtractionField[]>([]);
  const [crossFields, setCrossFields] = useState<CrossFieldConfig[]>([]);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (base.data) {
      setPromptText(base.data.prompt_text);
      setExtractionFields(base.data.extraction_fields);
      setCrossFields(base.data.cross_validation_config);
    }
  }, [base.data]);

  const mutation = useCreatePromptVersion();

  function onSubmit(event: React.FormEvent): void {
    event.preventDefault();
    setFormError(null);

    if (!tipoId) {
      setFormError("No se pudo determinar el tipo documental destino.");
      return;
    }
    if (!promptText.trim()) {
      setFormError("El prompt no puede estar vacio.");
      return;
    }
    if (extractionFields.length === 0) {
      setFormError("Definí al menos un campo a extraer.");
      return;
    }
    if (extractionFields.some((f) => !f.name.trim() || !f.label.trim())) {
      setFormError("Todos los campos a extraer deben tener nombre tecnico y etiqueta.");
      return;
    }
    // Descarta configs de validacion que quedaron huerfanas si el usuario
    // renombro o elimino el campo despues de habilitarle la validacion.
    const nombresVigentes = new Set(extractionFields.map((f) => f.name));
    const crossVigentes = crossFields.filter((cf) => nombresVigentes.has(cf.field));

    mutation.mutate(
      {
        tipo_documento_id: tipoId,
        prompt_text: promptText,
        extraction_fields: extractionFields,
        cross_validation_config: crossVigentes,
      },
      {
        onSuccess: (version) => {
          navigate(`/configuracion/tipos/${tipoId}/versiones/${version.id}`);
        },
      },
    );
  }

  if ((baseId && base.isLoading) || tipo.isLoading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-500">
        <Spinner size="lg" />
      </div>
    );
  }

  if (tipo.isError || !tipo.data) {
    return (
      <Alert variant="danger" title="No se pudo cargar el tipo documental">
        {extractApiMessage(tipo.error)}
      </Alert>
    );
  }

  if (baseId && base.isError) {
    return (
      <Alert variant="danger" title="No se pudo cargar la version base">
        {extractApiMessage(base.error)}
      </Alert>
    );
  }

  return (
    <form className="space-y-6" onSubmit={onSubmit}>
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-900">Nueva version</h1>
        <p className="text-sm text-slate-600">
          Tipo documental: <span className="font-medium">{tipo.data.nombre}</span>.{" "}
          {baseId
            ? "Edita una copia de la version seleccionada."
            : "Definí los campos que el modelo debe extraer, cargá el prompt y la configuración de validación cruzada."}{" "}
          Se crea como borrador y se publica desde el detalle.
        </p>
      </header>

      <section className="space-y-3 rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
          Campos a extraer
        </h2>
        <p className="text-xs text-slate-500">
          Son los campos que el modelo va a devolver para cada documento procesado.
          Definen el esquema de salida del LLM.
        </p>
        <ExtractionFieldsEditor value={extractionFields} onChange={setExtractionFields} />
      </section>

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
        <p className="text-xs text-slate-500">
          Por cada campo a extraer, decidí si se valida contra un valor de referencia
          enviado por el sistema integrador, qué normalizaciones aplicar y qué comparador usar.
        </p>
        <CrossFieldsEditor
          extractionFields={extractionFields}
          value={crossFields}
          onChange={setCrossFields}
        />
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
          onClick={() => navigate(`/configuracion/tipos/${tipoId}`)}
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
