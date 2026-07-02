import { useState, type ReactNode } from "react";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import { CrossValidationList } from "@/features/cases/components/CrossValidationList";
import { DecisionBadge } from "@/features/cases/components/DecisionBadge";
import { FileDropzone } from "@/features/cases/components/FileDropzone";
import { NormalizedFieldsTable } from "@/features/cases/components/NormalizedFieldsTable";
import { RuleResultsList } from "@/features/cases/components/RuleResultsList";
import { useSimulatePromptVersion } from "@/features/prompts/hooks/useSimulatePromptVersion";
import type {
  CrossFieldConfig,
  ExtractionField,
  SimulationResult,
} from "@/features/prompts/types";
import { extractApiMessage } from "@/lib/errors";
import { humanize } from "@/lib/strings";

interface SimulationPanelProps {
  versionId: string;
  extractionFields: ExtractionField[];
  crossFields: CrossFieldConfig[];
}

export function SimulationPanel({
  versionId,
  extractionFields,
  crossFields,
}: SimulationPanelProps): ReactNode {
  const labelsByName = Object.fromEntries(
    extractionFields.map((f) => [f.name, f.label]),
  );

  const [file, setFile] = useState<File | null>(null);
  const [expected, setExpected] = useState<Record<string, string>>(() =>
    Object.fromEntries(crossFields.map((cf) => [cf.field, ""])),
  );
  const [fileError, setFileError] = useState<string | null>(null);
  const mutation = useSimulatePromptVersion();

  function update(name: string, value: string): void {
    setExpected((prev) => ({ ...prev, [name]: value }));
  }

  function onSubmit(event: React.FormEvent): void {
    event.preventDefault();
    if (!file) {
      setFileError("Seleccioná un archivo para simular.");
      return;
    }
    setFileError(null);
    const cleaned = trimExpected(expected);
    mutation.mutate({ versionId, file, expected: cleaned });
  }

  function reset(): void {
    setFile(null);
    setExpected(Object.fromEntries(crossFields.map((cf) => [cf.field, ""])));
    mutation.reset();
  }

  return (
    <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-6">
      <header className="space-y-1">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
          Probar esta version
        </h2>
        <p className="text-xs text-slate-500">
          Procesa un documento de prueba con esta version del perfil. El pipeline es el mismo
          que el del sistema consumidor. La simulacion no queda registrada como caso.
        </p>
      </header>

      <form className="space-y-4" onSubmit={onSubmit}>
        <FileDropzone file={file} onChange={setFile} />
        {fileError && <p className="text-xs text-rose-700">{fileError}</p>}

        {crossFields.length > 0 && (
          <fieldset className="space-y-2">
            <legend className="text-xs font-medium text-slate-700">
              Datos de referencia para validacion cruzada
            </legend>
            <p className="text-xs text-slate-500">
              Los campos marcados con asterisco son requeridos por la configuracion de esta
              version. Si no se envia alguno requerido, el caso se rechaza antes de invocar al
              modelo.
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              {crossFields.map((cf) => {
                const label = labelsByName[cf.field] ?? humanize(cf.field);
                return (
                  <label key={cf.field} className="block space-y-1">
                    <span className="text-xs font-medium text-slate-700">
                      {label}
                      {cf.required_expected && <span className="text-rose-600"> *</span>}
                      {cf.critical && (
                        <span className="ml-1 text-xs font-normal text-slate-500">
                          (critico)
                        </span>
                      )}
                    </span>
                    <input
                      type="text"
                      value={expected[cf.field] ?? ""}
                      onChange={(e) => update(cf.field, e.target.value)}
                      className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                    />
                  </label>
                );
              })}
            </div>
          </fieldset>
        )}

        {mutation.error && (
          <Alert variant="danger" title="No se pudo simular">
            {extractApiMessage(mutation.error)}
          </Alert>
        )}

        <div className="flex items-center justify-between gap-2">
          <Button type="button" variant="secondary" onClick={reset}>
            Limpiar
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            Simular
          </Button>
        </div>
      </form>

      {mutation.data && <ResultPanel result={mutation.data} labels={labelsByName} />}
    </section>
  );
}

interface ResultPanelProps {
  result: SimulationResult;
  labels: Record<string, string>;
}

function ResultPanel({ result, labels }: ResultPanelProps): ReactNode {
  return (
    <div className="space-y-4 border-t border-slate-200 pt-4">
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-wide text-slate-500">Decision</p>
          <DecisionBadge veredicto={result.decision_status} />
        </div>
        <p className="text-right text-xs text-slate-500">Resultado de la simulacion</p>
      </div>

      {result.decision_reason && (
        <p className="text-sm text-slate-700">{result.decision_reason}</p>
      )}

      {result.normalized_extraction && (
        <section className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-600">
            Datos extraidos
          </h3>
          <NormalizedFieldsTable data={result.normalized_extraction} labels={labels} />
        </section>
      )}

      {result.rule_results && result.rule_results.length > 0 && (
        <section className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-600">
            Reglas internas
          </h3>
          <RuleResultsList results={result.rule_results} />
        </section>
      )}

      {result.cross_validation_results && result.cross_validation_results.length > 0 && (
        <section className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-600">
            Validacion cruzada
          </h3>
          <CrossValidationList results={result.cross_validation_results} />
        </section>
      )}
    </div>
  );
}

function trimExpected(values: Record<string, string>): Record<string, string> | null {
  const cleaned: Record<string, string> = {};
  for (const [key, value] of Object.entries(values)) {
    if (value && value.trim() !== "") {
      cleaned[key] = value.trim();
    }
  }
  return Object.keys(cleaned).length === 0 ? null : cleaned;
}
