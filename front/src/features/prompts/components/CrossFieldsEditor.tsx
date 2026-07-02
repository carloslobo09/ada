import type { ReactNode } from "react";
import {
  COMPARISON_OPTIONS,
  NORMALIZATION_OPTIONS,
  type ComparisonType,
  type CrossFieldConfig,
  type ExtractionField,
  type NormalizationType,
} from "@/features/prompts/types";

interface CrossFieldsEditorProps {
  extractionFields: ExtractionField[];
  value: CrossFieldConfig[];
  onChange: (value: CrossFieldConfig[]) => void;
  readOnly?: boolean;
}

const DEFAULT_CONFIG: Omit<CrossFieldConfig, "field"> = {
  normalization: [],
  comparison: "equals",
  critical: false,
  required_expected: false,
};

export function CrossFieldsEditor({
  extractionFields,
  value,
  onChange,
  readOnly = false,
}: CrossFieldsEditorProps): ReactNode {
  if (extractionFields.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        Definí primero los campos a extraer. La validación cruzada solo opera sobre los
        campos que el modelo va a devolver.
      </p>
    );
  }

  const configByName = new Map(value.map((cf) => [cf.field, cf]));

  function syncOrder(updated: Map<string, CrossFieldConfig>): CrossFieldConfig[] {
    return extractionFields
      .map((ef) => updated.get(ef.name))
      .filter((cf): cf is CrossFieldConfig => cf !== undefined);
  }

  function toggleField(name: string, enabled: boolean): void {
    const next = new Map(configByName);
    if (enabled) {
      next.set(name, { field: name, ...DEFAULT_CONFIG });
    } else {
      next.delete(name);
    }
    onChange(syncOrder(next));
  }

  function updateField(name: string, patch: Partial<CrossFieldConfig>): void {
    const current = configByName.get(name);
    if (!current) return;
    const next = new Map(configByName);
    next.set(name, { ...current, ...patch });
    onChange(syncOrder(next));
  }

  function toggleNormalization(name: string, norm: NormalizationType): void {
    const current = configByName.get(name);
    if (!current) return;
    const list = current.normalization;
    const next = list.includes(norm)
      ? list.filter((n) => n !== norm)
      : [...list, norm];
    updateField(name, { normalization: next });
  }

  if (readOnly && value.length === 0) {
    return <p className="text-sm text-slate-500">Sin validaciones cruzadas configuradas.</p>;
  }

  const fieldsToRender = readOnly
    ? extractionFields.filter((ef) => configByName.has(ef.name))
    : extractionFields;

  return (
    <div className="space-y-3">
      {fieldsToRender.map((ef) => {
        const cfg = configByName.get(ef.name);
        const enabled = Boolean(cfg);
        return (
          <div
            key={ef.name}
            className="space-y-3 rounded-md border border-slate-200 bg-white p-4"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-slate-900">{ef.label}</p>
                <p className="font-mono text-xs text-slate-500">{ef.name}</p>
              </div>
              {!readOnly && (
                <label className="flex items-center gap-2 text-xs font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={enabled}
                    onChange={(e) => toggleField(ef.name, e.target.checked)}
                  />
                  Validar este campo
                </label>
              )}
            </div>

            {enabled && cfg && (
              <>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block space-y-1">
                    <span className="text-xs font-medium text-slate-700">Comparador</span>
                    {readOnly ? (
                      <p className="text-sm text-slate-700">{labelOf(cfg.comparison)}</p>
                    ) : (
                      <select
                        value={cfg.comparison}
                        onChange={(e) =>
                          updateField(ef.name, {
                            comparison: e.target.value as ComparisonType,
                          })
                        }
                        className="w-full rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                      >
                        {COMPARISON_OPTIONS.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    )}
                  </label>
                </div>

                <div className="space-y-1">
                  <span className="text-xs font-medium text-slate-700">
                    Normalizaciones{" "}
                    <span className="text-slate-400">
                      (se aplican en orden a ambos valores antes de comparar)
                    </span>
                  </span>
                  {readOnly ? (
                    cfg.normalization.length === 0 ? (
                      <p className="text-xs text-slate-500">Sin normalizaciones.</p>
                    ) : (
                      <ol className="list-decimal pl-5 text-xs text-slate-700">
                        {cfg.normalization.map((n) => (
                          <li key={n}>{labelOfNorm(n)}</li>
                        ))}
                      </ol>
                    )
                  ) : (
                    <div className="flex flex-wrap gap-x-1.5 gap-y-3 pt-2">
                      {NORMALIZATION_OPTIONS.map((opt) => {
                        const order = cfg.normalization.indexOf(opt.value);
                        const active = order >= 0;
                        return (
                          <button
                            key={opt.value}
                            type="button"
                            onClick={() => toggleNormalization(ef.name, opt.value)}
                            className={`relative rounded-full border px-2.5 py-1 text-xs font-medium transition-colors ${
                              active
                                ? "border-brand-500 bg-brand-50 text-brand-700"
                                : "border-slate-300 bg-white text-slate-600 hover:bg-slate-50"
                            }`}
                          >
                            {active && (
                              <span className="absolute -top-2 -left-2 inline-flex h-4 w-4 items-center justify-center rounded-full bg-brand-600 text-[10px] font-semibold text-white shadow-sm">
                                {order + 1}
                              </span>
                            )}
                            {opt.label}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-4 text-sm">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={cfg.critical}
                      disabled={readOnly}
                      onChange={(e) =>
                        updateField(ef.name, { critical: e.target.checked })
                      }
                    />
                    <span className="text-slate-700">Critico</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={cfg.required_expected}
                      disabled={readOnly}
                      onChange={(e) =>
                        updateField(ef.name, { required_expected: e.target.checked })
                      }
                    />
                    <span className="text-slate-700">
                      Obligatorio en el payload del cliente
                    </span>
                  </label>
                </div>

                {cfg.critical && !cfg.required_expected && (
                  <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                    Este campo es critico pero no obligatorio: si el integrador no lo
                    envia, la comparacion no se ejecuta y el caso puede aprobarse sin
                    este control. Marcalo tambien como obligatorio si el cruce debe
                    cumplirse siempre.
                  </p>
                )}
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}

function labelOf(value: ComparisonType): string {
  return COMPARISON_OPTIONS.find((opt) => opt.value === value)?.label ?? value;
}

function labelOfNorm(value: NormalizationType): string {
  return NORMALIZATION_OPTIONS.find((opt) => opt.value === value)?.label ?? value;
}
