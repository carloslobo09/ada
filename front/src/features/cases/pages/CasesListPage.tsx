import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Alert } from "@/components/Alert";
import { Spinner } from "@/components/Spinner";
import { DecisionBadge } from "@/features/cases/components/DecisionBadge";
import { RecontrolBadge } from "@/features/cases/components/RecontrolBadge";
import { useListCases } from "@/features/cases/hooks/useListCases";

export function CasesListPage(): ReactNode {
  const { data, isLoading, isError, error } = useListCases();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-500">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <Alert variant="danger" title="No se pudo cargar la lista de casos">
        {error instanceof Error ? error.message : "Error desconocido."}
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-900">Casos</h1>
        <p className="text-sm text-slate-600">
          Listado de los ultimos casos procesados por la plataforma.
        </p>
      </header>

      {data.items.length === 0 ? (
        <Alert variant="info">No hay casos procesados todavia.</Alert>
      ) : (
        <ul className="divide-y divide-slate-100 overflow-hidden rounded-lg border border-slate-200 bg-white">
          {data.items.map((item) => (
            <li key={item.id}>
              <Link
                to={`/casos/${item.id}`}
                className="flex items-center justify-between gap-4 px-5 py-3 transition-colors hover:bg-slate-50"
              >
                <div>
                  <p className="text-sm font-medium text-slate-900">
                    Caso #{item.id.slice(0, 8)}
                  </p>
                  <p className="text-xs text-slate-500">
                    {new Date(item.fecha_creacion).toLocaleString("es-AR")} - {item.estado}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <RecontrolBadge estado={item.estado_recontrol} />
                  <DecisionBadge veredicto={item.decision?.veredicto ?? null} />
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
