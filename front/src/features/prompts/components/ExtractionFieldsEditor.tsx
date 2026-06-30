import type { ReactNode } from "react";
import type { ExtractionField } from "@/features/prompts/types";

interface ExtractionFieldsEditorProps {
  value: ExtractionField[];
  onChange: (value: ExtractionField[]) => void;
  readOnly?: boolean;
}

const NEW_FIELD: ExtractionField = { name: "", label: "" };

export function ExtractionFieldsEditor({
  value,
  onChange,
  readOnly = false,
}: ExtractionFieldsEditorProps): ReactNode {
  function update(index: number, patch: Partial<ExtractionField>): void {
    onChange(value.map((item, i) => (i === index ? { ...item, ...patch } : item)));
  }

  function remove(index: number): void {
    onChange(value.filter((_, i) => i !== index));
  }

  function add(): void {
    onChange([...value, { ...NEW_FIELD }]);
  }

  if (value.length === 0 && readOnly) {
    return <p className="text-sm text-slate-500">Sin campos definidos.</p>;
  }

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-md border border-slate-200 bg-white">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2 text-left font-semibold">Nombre tecnico</th>
              <th className="px-3 py-2 text-left font-semibold">Etiqueta visible</th>
              {!readOnly && <th className="px-3 py-2" />}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {value.length === 0 && (
              <tr>
                <td colSpan={readOnly ? 2 : 3} className="px-3 py-4 text-center text-slate-500">
                  Sin campos definidos.
                </td>
              </tr>
            )}
            {value.map((item, index) => (
              <tr key={index}>
                <td className="px-3 py-2">
                  {readOnly ? (
                    <span className="font-mono text-xs text-slate-700">{item.name}</span>
                  ) : (
                    <input
                      type="text"
                      value={item.name}
                      onChange={(e) =>
                        update(index, { name: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, "_") })
                      }
                      placeholder="numero_dni"
                      className="w-full rounded-md border border-slate-300 px-2 py-1 font-mono text-xs focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                    />
                  )}
                </td>
                <td className="px-3 py-2">
                  {readOnly ? (
                    <span className="text-slate-700">{item.label}</span>
                  ) : (
                    <input
                      type="text"
                      value={item.label}
                      onChange={(e) => update(index, { label: e.target.value })}
                      placeholder="Numero de DNI"
                      className="w-full rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                    />
                  )}
                </td>
                {!readOnly && (
                  <td className="px-3 py-2 text-right">
                    <button
                      type="button"
                      onClick={() => remove(index)}
                      className="text-xs font-medium text-rose-700 hover:underline"
                    >
                      Quitar
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!readOnly && (
        <button
          type="button"
          onClick={add}
          className="w-full rounded-md border border-dashed border-slate-300 px-3 py-2 text-xs font-medium text-slate-600 hover:border-brand-500 hover:text-brand-700"
        >
          + Agregar campo
        </button>
      )}
      <p className="text-xs text-slate-500">
        El nombre tecnico es el que el modelo devuelve y el sistema persiste. Solo letras minusculas, digitos y guion bajo.
        La etiqueta es para mostrar al usuario en esta plataforma.
      </p>
    </div>
  );
}
