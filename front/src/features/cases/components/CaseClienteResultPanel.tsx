import type { ReactNode } from "react";
import { DecisionBadge } from "@/features/cases/components/DecisionBadge";
import { NormalizedFieldsTable } from "@/features/cases/components/NormalizedFieldsTable";
import type { CaseCliente } from "@/features/cases/types";

interface CaseClienteResultPanelProps {
  caso: CaseCliente;
}

export function CaseClienteResultPanel({ caso }: CaseClienteResultPanelProps): ReactNode {
  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-wide text-slate-500">Decision</p>
            <DecisionBadge veredicto={caso.veredicto} />
          </div>
          <div className="text-right text-xs text-slate-500">
            <p>Caso #{caso.id.slice(0, 8)}</p>
            <p>{new Date(caso.fecha_creacion).toLocaleString("es-AR")}</p>
            <p>
              Estado: <span className="font-medium">{caso.estado}</span>
            </p>
          </div>
        </div>
        {caso.motivos && <p className="mt-3 text-sm text-slate-700">{caso.motivos}</p>}
      </section>

      {caso.documento && (
        <Section title="Documento recibido">
          <dl className="grid gap-y-2 gap-x-6 rounded-md border border-slate-200 bg-white p-4 sm:grid-cols-2">
            <Detail label="Archivo" value={caso.documento.nombre_archivo} />
            <Detail label="Tipo" value={caso.documento.content_type} />
            <Detail
              label="Tamano"
              value={`${(caso.documento.file_size / 1024).toFixed(1)} KB`}
            />
            <Detail
              label="Recepcion"
              value={new Date(caso.documento.fecha_recepcion).toLocaleString("es-AR")}
            />
          </dl>
        </Section>
      )}

      {caso.campos_extraidos && Object.keys(caso.campos_extraidos).length > 0 && (
        <Section title="Datos extraidos">
          <NormalizedFieldsTable data={caso.campos_extraidos} />
        </Section>
      )}

      {caso.validaciones_cruzadas && caso.validaciones_cruzadas.length > 0 && (
        <Section title="Validaciones con tus datos de referencia">
          <ul className="divide-y divide-slate-100 overflow-hidden rounded-md border border-slate-200 bg-white">
            {caso.validaciones_cruzadas.map((v) => (
              <li key={v.field} className="flex items-start justify-between gap-3 px-4 py-3">
                <div className="space-y-0.5">
                  <p className="text-sm font-medium text-slate-900">{v.field}</p>
                  <p className="text-xs text-slate-500">
                    Esperado: <span className="font-mono text-slate-700">{v.expected}</span>
                  </p>
                  <p className="text-xs text-slate-500">
                    Extraido: <span className="font-mono text-slate-700">{v.extracted || "-"}</span>
                  </p>
                  {!v.passed && (
                    <p className="text-xs text-rose-700">{v.reason}</p>
                  )}
                </div>
                <span
                  className={`inline-flex shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide ${
                    v.passed
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-rose-100 text-rose-800"
                  }`}
                >
                  {v.passed ? "Coincide" : "No coincide"}
                </span>
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }): ReactNode {
  return (
    <section className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">{title}</h2>
      {children}
    </section>
  );
}

function Detail({ label, value }: { label: string; value: string }): ReactNode {
  return (
    <div className="flex flex-col">
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="break-all text-sm text-slate-900">{value}</dd>
    </div>
  );
}
