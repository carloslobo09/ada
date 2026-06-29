import type { ReactNode } from "react";

interface NormalizedFieldsTableProps {
  data: Record<string, unknown>;
}

const FIELD_ORDER = [
  "numero_dni",
  "nombre_completo",
  "fecha_nacimiento",
  "fecha_emision",
  "fecha_vencimiento",
  "sexo",
  "nacionalidad",
  "lugar_nacimiento",
  "numero_tramite",
  "tipo_documento",
  "domicilio",
  "dorso_presente",
];

const LABELS: Record<string, string> = {
  numero_dni: "Numero de DNI",
  nombre_completo: "Nombre completo",
  fecha_nacimiento: "Fecha de nacimiento",
  fecha_emision: "Fecha de emision",
  fecha_vencimiento: "Fecha de vencimiento",
  sexo: "Sexo",
  nacionalidad: "Nacionalidad",
  lugar_nacimiento: "Lugar de nacimiento",
  numero_tramite: "Numero de tramite",
  tipo_documento: "Tipo de documento",
  domicilio: "Domicilio",
  dorso_presente: "Dorso presente",
};

export function NormalizedFieldsTable({ data }: NormalizedFieldsTableProps): ReactNode {
  const knownKeys = FIELD_ORDER.filter((key) => key in data && key !== "confianzas");
  const extras = Object.keys(data).filter((key) => !FIELD_ORDER.includes(key) && key !== "confianzas");
  const orderedKeys = [...knownKeys, ...extras];

  return (
    <dl className="grid gap-y-3 gap-x-6 rounded-md border border-slate-200 bg-white p-4 sm:grid-cols-2">
      {orderedKeys.map((key) => {
        const value = data[key];
        return (
          <div key={key} className="flex flex-col">
            <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
              {LABELS[key] ?? key}
            </dt>
            <dd className="text-sm text-slate-900">{formatValue(value)}</dd>
          </div>
        );
      })}
    </dl>
  );
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "boolean") return value ? "Si" : "No";
  return String(value);
}
