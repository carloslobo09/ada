import type { ReactNode } from "react";
import type { Case } from "@/features/cases/types";
import { DecisionBadge } from "@/features/cases/components/DecisionBadge";
import { RuleResultsList } from "@/features/cases/components/RuleResultsList";
import { CrossValidationList } from "@/features/cases/components/CrossValidationList";
import { NormalizedFieldsTable } from "@/features/cases/components/NormalizedFieldsTable";

interface CaseResultPanelProps {
  caso: Case;
}

export function CaseResultPanel({ caso }: CaseResultPanelProps): ReactNode {
  const decision = caso.decision;
  const refs = decision?.refs_evidencias ?? null;

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-wide text-slate-500">Decision</p>
            <DecisionBadge veredicto={decision?.veredicto ?? null} />
          </div>
          <div className="text-right text-xs text-slate-500">
            <p>Caso #{caso.id.slice(0, 8)}</p>
            <p>{new Date(caso.fecha_creacion).toLocaleString("es-AR")}</p>
            <p>
              Estado del caso: <span className="font-medium">{caso.estado}</span>
            </p>
          </div>
        </div>
        {decision?.motivos && (
          <p className="mt-3 text-sm text-slate-700">{decision.motivos}</p>
        )}
        {decision?.confianza_global !== null && decision?.confianza_global !== undefined && (
          <p className="mt-2 text-xs text-slate-500">
            Confianza global: <span className="font-medium">{decision.confianza_global.toFixed(2)}</span>
          </p>
        )}
      </section>

      {caso.documento && (
        <Section title="Documento recibido">
          <dl className="grid gap-y-2 gap-x-6 rounded-md border border-slate-200 bg-white p-4 sm:grid-cols-2">
            <Detail label="Tipo de documento" value={caso.documento.tipo_documento_id} />
            <Detail label="Hash integridad" value={caso.documento.hash_integridad} />
            <Detail label="Ubicacion" value={caso.documento.ubicacion_s3} />
            <Detail
              label="Recepcion"
              value={new Date(caso.documento.fecha_recepcion).toLocaleString("es-AR")}
            />
            <Detail label="MIME" value={caso.documento.content_type} />
            <Detail label="Tamano" value={`${(caso.documento.file_size / 1024).toFixed(1)} KB`} />
          </dl>
        </Section>
      )}

      {refs?.resultado_extraccion?.campos_normalizados && (
        <Section title="Datos extraidos">
          <NormalizedFieldsTable data={refs.resultado_extraccion.campos_normalizados} />
        </Section>
      )}

      {refs?.evaluacion_reglas && refs.evaluacion_reglas.length > 0 && (
        <Section title="Reglas internas">
          <RuleResultsList results={refs.evaluacion_reglas} />
        </Section>
      )}

      {decision?.cross_validation_results && decision.cross_validation_results.length > 0 && (
        <Section title="Validacion cruzada">
          <CrossValidationList results={decision.cross_validation_results} />
        </Section>
      )}

      {decision?.expected_received && Object.keys(decision.expected_received).length > 0 && (
        <Section title="Datos recibidos del cliente">
          <pre className="overflow-x-auto rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700">
            {JSON.stringify(decision.expected_received, null, 2)}
          </pre>
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
