import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Alert } from "@/components/Alert";
import { Spinner } from "@/components/Spinner";
import { PromptVersionsTable } from "@/features/prompts/components/PromptVersionsTable";
import { useListPromptVersions } from "@/features/prompts/hooks/useListPromptVersions";

export function PromptVersionsPage(): ReactNode {
  const { data, isLoading, isError, error } = useListPromptVersions();

  return (
    <div className="space-y-6">
      <header className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold text-slate-900">Configuracion</h1>
          <p className="text-sm text-slate-600">
            Versiones del perfil de validacion. La version activa es la que la plataforma usa
            para procesar nuevos casos.
          </p>
        </div>
        <Link
          to="/configuracion/nueva"
          className="inline-flex items-center gap-2 rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          Nueva version
        </Link>
      </header>

      {isLoading && (
        <div className="flex items-center justify-center py-20 text-slate-500">
          <Spinner size="lg" />
        </div>
      )}

      {isError && (
        <Alert variant="danger" title="No se pudieron cargar las versiones">
          {error instanceof Error ? error.message : "Error desconocido."}
        </Alert>
      )}

      {data && <PromptVersionsTable versions={data} />}
    </div>
  );
}
