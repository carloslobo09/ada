import type { ReactNode } from "react";
import {
  COMPARISON_OPTIONS,
  type ComparisonType,
  type CrossFieldConfig,
} from "@/features/prompts/types";

interface CrossFieldsEditorProps {
  value: CrossFieldConfig[];
  onChange: (value: CrossFieldConfig[]) => void;
  readOnly?: boolean;
}

const NEW_FIELD: CrossFieldConfig = {
  field: "",
  comparison: "equals",
  critical: false,
  required_expected: false,
};

export function CrossFieldsEditor({
  value,
  onChange,
  readOnly = false,
}: CrossFieldsEditorProps): ReactNode {
  function update(index: number, patch: Partial<CrossFieldConfig>): void {
    const next = value.map((item, i) => (i === index ? { ...item, ...patch } : item));
    onChange(next);
  }

  function remove(index: number): void {
    onChange(value.filter((_, i) => i !== index));
  }

  function add(): void {
    onChange([...value, { ...NEW_FIELD }]);
  }

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-md border border-slate-200 bg-white">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2 text-left font-semibold">Campo</th>
              <th className="px-3 py-2 text-left font-semibold">Comparador</th>
              <th className="px-3 py-2 text-center font-semibold">Critico</th>
              <th className="px-3 py-2 text-center font-semibold">Obligatorio</th>
              {!readOnly && <th className="px-3 py-2" />}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {value.length === 0 && (
              <tr>
                <td colSpan={readOnly ? 4 : 5} className="px-3 py-4 text-center text-slate-500">
                  Sin campos configurados.
                </td>
              </tr>
            )}
            {value.map((item, index) => (
              <tr key={index}>
                <td className="px-3 py-2">
                  {readOnly ? (
                    <span className="font-medium text-slate-900">{item.field}</span>
                  ) : (
                    <input
                      type="text"
                      value={item.field}
                      onChange={(e) => update(index, { field: e.target.value })}
                      placeholder="numero_dni"
                      className="w-full rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                    />
                  )}
                </td>
                <td className="px-3 py-2">
                  {readOnly ? (
                    <span className="text-slate-700">{labelOf(item.comparison)}</span>
                  ) : (
                    <select
                      value={item.comparison}
                      onChange={(e) =>
                        update(index, { comparison: e.target.value as ComparisonType })
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
                </td>
                <td className="px-3 py-2 text-center">
                  <input
                    type="checkbox"
                    checked={item.critical}
                    disabled={readOnly}
                    onChange={(e) => update(index, { critical: e.target.checked })}
                  />
                </td>
                <td className="px-3 py-2 text-center">
                  <input
                    type="checkbox"
                    checked={item.required_expected}
                    disabled={readOnly}
                    onChange={(e) => update(index, { required_expected: e.target.checked })}
                  />
                </td>
                {!readOnly && (
                  <td className="px-3 py-2 text-right">
                    <button
                      type="button"
                      onClick={() => remove(index)}
                      className="text-xs text-rose-700 hover:underline"
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
          className="rounded-md border border-dashed border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-brand-500 hover:text-brand-700"
        >
          + Agregar campo
        </button>
      )}
    </div>
  );
}

function labelOf(value: ComparisonType): string {
  return COMPARISON_OPTIONS.find((opt) => opt.value === value)?.label ?? value;
}
