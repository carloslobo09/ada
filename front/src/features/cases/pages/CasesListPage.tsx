import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { Alert } from "@/components/Alert";
import { Spinner } from "@/components/Spinner";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { DecisionBadge } from "@/features/cases/components/DecisionBadge";
import { RecontrolBadge } from "@/features/cases/components/RecontrolBadge";
import { useListCases, useListCasesCliente } from "@/features/cases/hooks/useListCases";
import type {
  CaseClienteListItem,
  CasesListItem,
  EstadoRecontrol,
} from "@/features/cases/types";
import { DashboardPanel } from "@/features/metrics/components/DashboardPanel";

type Tab = EstadoRecontrol | "todos";

const TABS: { id: Tab; label: string; description: string }[] = [
  {
    id: "pendiente",
    label: "Sin revisar",
    description:
      "Casos emitidos por la plataforma que aun no fueron revisados por el entrenador.",
  },
  {
    id: "incorrecto",
    label: "Con observacion",
    description:
      "Casos en los que el entrenador marco el analisis como incorrecto. Insumo para la siguiente version del prompt.",
  },
  {
    id: "todos",
    label: "Todos",
    description: "Todos los casos sin filtrar por estado de Re Control.",
  },
];

export function CasesListPage(): ReactNode {
  const { user } = useAuth();
  const isEntrenador = user?.rol === "entrenador" || user?.rol === "admin";

  return isEntrenador ? <EntrenadorView /> : <ClienteView />;
}

function EntrenadorView(): ReactNode {
  const [tab, setTab] = useState<Tab>("pendiente");
  const params = tab === "todos" ? {} : { recontrol: tab };
  const { data, isLoading, isError, error } = useListCases(params);
  const current = TABS.find((t) => t.id === tab) as (typeof TABS)[number];

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-900">Re Control</h1>
        <p className="text-sm text-slate-600">
          Panel operativo del entrenador: indicadores de proceso y bandeja de casos para
          revisar.
        </p>
      </header>

      <DashboardPanel />

      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
          Bandeja de casos
        </h2>

        <nav className="flex flex-wrap gap-1 rounded-lg border border-slate-200 bg-white p-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                tab === t.id
                  ? "bg-brand-50 text-brand-700"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>

        <p className="text-xs text-slate-500">{current.description}</p>

        {isLoading && (
          <div className="flex items-center justify-center py-12 text-slate-500">
            <Spinner size="lg" />
          </div>
        )}

        {isError && (
          <Alert variant="danger" title="No se pudo cargar la bandeja">
            {error instanceof Error ? error.message : "Error desconocido."}
          </Alert>
        )}

        {data && data.items.length === 0 && (
          <Alert variant="info">No hay casos en esta vista.</Alert>
        )}

        {data && data.items.length > 0 && <CasesList items={data.items} />}
      </section>
    </div>
  );
}

function ClienteView(): ReactNode {
  const { data, isLoading, isError, error } = useListCasesCliente();

  return (
    <div className="space-y-4">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-900">Mis casos</h1>
        <p className="text-sm text-slate-600">
          Listado de los documentos que enviaste a la plataforma y la decision asociada.
        </p>
      </header>

      {isLoading && (
        <div className="flex items-center justify-center py-12 text-slate-500">
          <Spinner size="lg" />
        </div>
      )}

      {isError && (
        <Alert variant="danger" title="No se pudo cargar la lista">
          {error instanceof Error ? error.message : "Error desconocido."}
        </Alert>
      )}

      {data && data.items.length === 0 && (
        <Alert variant="info">Aun no enviaste casos.</Alert>
      )}

      {data && data.items.length > 0 && <ClientesCasesList items={data.items} />}
    </div>
  );
}

function ClientesCasesList({ items }: { items: CaseClienteListItem[] }): ReactNode {
  return (
    <ul className="divide-y divide-slate-100 overflow-hidden rounded-lg border border-slate-200 bg-white">
      {items.map((item) => (
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
            <DecisionBadge veredicto={item.veredicto} />
          </Link>
        </li>
      ))}
    </ul>
  );
}

function CasesList({ items }: { items: CasesListItem[] }): ReactNode {
  return (
    <ul className="divide-y divide-slate-100 overflow-hidden rounded-lg border border-slate-200 bg-white">
      {items.map((item) => (
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
  );
}
