import { useMemo, useState, type ReactNode } from "react";
import { Alert } from "@/components/Alert";
import { Spinner } from "@/components/Spinner";
import { HorizontalBar } from "@/features/metrics/components/HorizontalBar";
import { KpiCard } from "@/features/metrics/components/KpiCard";
import { Sparkline } from "@/features/metrics/components/Sparkline";
import { useDashboardMetrics } from "@/features/metrics/hooks/useDashboardMetrics";
import { extractApiMessage } from "@/lib/errors";

const PRESETS = [
  { label: "7 dias", days: 7 },
  { label: "30 dias", days: 30 },
  { label: "Hoy", days: 1 },
] as const;

function defaultRange(): { desde: string; hasta: string } {
  const today = new Date();
  const hasta = isoDate(today);
  const desde = isoDate(addDays(today, -6));
  return { desde, hasta };
}

function isoDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function addDays(d: Date, days: number): Date {
  const next = new Date(d);
  next.setDate(d.getDate() + days);
  return next;
}

export function DashboardPanel(): ReactNode {
  const [range, setRange] = useState(defaultRange);

  const { data, isLoading, isError, error, isFetching } = useDashboardMetrics(range);

  const totalDistribucion = useMemo(() => {
    if (!data) return 0;
    const d = data.distribucion_decisiones;
    return d.aprobados + d.rechazados + d.rechazados_pre_llm;
  }, [data]);

  function applyPreset(days: number): void {
    const today = new Date();
    setRange({
      desde: isoDate(addDays(today, -(days - 1))),
      hasta: isoDate(today),
    });
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-3 rounded-lg border border-slate-200 bg-white p-3">
        <div className="flex flex-wrap items-end gap-3">
          <label className="block space-y-1">
            <span className="text-xs font-medium text-slate-700">Desde</span>
            <input
              type="date"
              value={range.desde}
              max={range.hasta}
              onChange={(e) => setRange((r) => ({ ...r, desde: e.target.value }))}
              className="rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </label>
          <label className="block space-y-1">
            <span className="text-xs font-medium text-slate-700">Hasta</span>
            <input
              type="date"
              value={range.hasta}
              min={range.desde}
              max={isoDate(new Date())}
              onChange={(e) => setRange((r) => ({ ...r, hasta: e.target.value }))}
              className="rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </label>
        </div>

        <div className="flex flex-wrap items-end gap-3">
          <div className="space-y-1">
            <span className="block text-xs font-medium text-slate-700">Vista rapida</span>
            <div className="inline-flex overflow-hidden rounded-md border border-slate-300 bg-white">
              {PRESETS.map((p, idx) => (
                <button
                  key={p.label}
                  type="button"
                  onClick={() => applyPreset(p.days)}
                  className={`px-2.5 py-1 text-xs font-medium text-slate-700 transition-colors hover:bg-slate-50 ${
                    idx > 0 ? "border-l border-slate-300" : ""
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
          {isFetching && !isLoading && (
            <span className="pb-1 text-xs text-slate-500">Actualizando...</span>
          )}
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center rounded-lg border border-slate-200 bg-white py-12 text-slate-500">
          <Spinner size="md" />
        </div>
      )}

      {isError && (
        <Alert variant="danger" title="No se pudieron cargar las metricas">
          {extractApiMessage(error)}
        </Alert>
      )}

      {data && (
        <>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <KpiCard label="Casos totales" value={data.kpis.total_casos.toString()} />
            <KpiCard
              label="Aprobados"
              value={`${data.kpis.porcentaje_aprobados.toFixed(1)}%`}
              hint={`Rechazados: ${data.kpis.porcentaje_rechazados.toFixed(1)}%`}
            />
            <KpiCard
              label="Pendientes Re Control"
              value={data.kpis.pendientes_recontrol.toString()}
            />
            <KpiCard
              label="Acuerdo IA / humano"
              value={
                data.kpis.porcentaje_acuerdo_ia_humano !== null
                  ? `${data.kpis.porcentaje_acuerdo_ia_humano.toFixed(1)}%`
                  : "-"
              }
              hint={
                data.kpis.porcentaje_acuerdo_ia_humano !== null
                  ? `Sobre los casos ya revisados`
                  : `Sin casos revisados todavia`
              }
            />
            <KpiCard
              label="Confianza promedio"
              value={
                data.kpis.confianza_promedio !== null
                  ? data.kpis.confianza_promedio.toFixed(2)
                  : "-"
              }
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="space-y-3 rounded-lg border border-slate-200 bg-white p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                Distribucion de decisiones
              </h3>
              {totalDistribucion === 0 ? (
                <p className="text-xs text-slate-500">Sin casos en el rango.</p>
              ) : (
                <div className="space-y-2">
                  <HorizontalBar
                    label="Aprobados"
                    value={data.distribucion_decisiones.aprobados}
                    total={totalDistribucion}
                    color="emerald"
                  />
                  <HorizontalBar
                    label="Rechazados"
                    value={data.distribucion_decisiones.rechazados}
                    total={totalDistribucion}
                    color="rose"
                  />
                  <HorizontalBar
                    label="Rechazados pre-LLM"
                    value={data.distribucion_decisiones.rechazados_pre_llm}
                    total={totalDistribucion}
                    color="slate"
                  />
                </div>
              )}
            </div>

            <div className="space-y-3 rounded-lg border border-slate-200 bg-white p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                Acuerdo IA / humano
              </h3>
              {data.acuerdo_ia_humano.revisados === 0 ? (
                <p className="text-xs text-slate-500">
                  No hay casos revisados en el rango.
                </p>
              ) : (
                <div className="space-y-2">
                  <HorizontalBar
                    label="IA acerto (correctos)"
                    value={data.acuerdo_ia_humano.correctos}
                    total={data.acuerdo_ia_humano.revisados}
                    color="emerald"
                  />
                  <HorizontalBar
                    label="IA fallo (incorrectos)"
                    value={data.acuerdo_ia_humano.incorrectos}
                    total={data.acuerdo_ia_humano.revisados}
                    color="rose"
                  />
                  {data.acuerdo_ia_humano.incorrectos > 0 && (
                    <div className="grid grid-cols-2 gap-2 pt-2 text-xs text-slate-600">
                      <div className="rounded border border-slate-200 bg-slate-50 px-2 py-1.5">
                        <p className="text-[10px] uppercase tracking-wide text-slate-500">
                          Falsos positivos
                        </p>
                        <p className="font-semibold text-slate-900">
                          {data.acuerdo_ia_humano.falsos_positivos}
                        </p>
                        <p className="text-[10px] text-slate-500">
                          IA aprobo, humano marco incorrecto
                        </p>
                      </div>
                      <div className="rounded border border-slate-200 bg-slate-50 px-2 py-1.5">
                        <p className="text-[10px] uppercase tracking-wide text-slate-500">
                          Falsos negativos
                        </p>
                        <p className="font-semibold text-slate-900">
                          {data.acuerdo_ia_humano.falsos_negativos}
                        </p>
                        <p className="text-[10px] text-slate-500">
                          IA rechazo, humano marco incorrecto
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="space-y-3 rounded-lg border border-slate-200 bg-white p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                Top motivos de rechazo
              </h3>
              {data.top_motivos_rechazo.length === 0 ? (
                <p className="text-xs text-slate-500">Sin rechazos en el rango.</p>
              ) : (
                <ol className="space-y-1.5 text-sm">
                  {data.top_motivos_rechazo.map((m, idx) => (
                    <li
                      key={m.motivo}
                      className="flex items-center justify-between gap-3 border-b border-slate-100 pb-1.5 last:border-0 last:pb-0"
                    >
                      <span className="flex items-center gap-2">
                        <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-slate-100 text-xs font-medium text-slate-600">
                          {idx + 1}
                        </span>
                        <span className="font-mono text-xs text-slate-700">
                          {m.motivo}
                        </span>
                      </span>
                      <span className="text-xs font-medium text-slate-900">
                        {m.cantidad}
                      </span>
                    </li>
                  ))}
                </ol>
              )}
            </div>

            <div className="space-y-3 rounded-lg border border-slate-200 bg-white p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                Casos por dia
              </h3>
              <Sparkline serie={data.casos_por_dia} />
              <p className="text-[10px] text-slate-500">
                Pasar el cursor sobre una barra para ver fecha y cantidad.
              </p>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
