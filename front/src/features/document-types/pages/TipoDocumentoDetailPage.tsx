import type { ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { Alert } from "@/components/Alert";
import { Spinner } from "@/components/Spinner";
import { useGetTipoDocumento } from "@/features/document-types/hooks/useGetTipoDocumento";
import { PromptVersionsTable } from "@/features/prompts/components/PromptVersionsTable";
import { useListPromptVersions } from "@/features/prompts/hooks/useListPromptVersions";
import { extractApiMessage } from "@/lib/errors";

export function TipoDocumentoDetailPage(): ReactNode {
  const { tipoId } = useParams<{ tipoId: string }>();
  const tipo = useGetTipoDocumento(tipoId);
  const versiones = useListPromptVersions(tipoId);

  if (tipo.isLoading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-500">
        <Spinner size="lg" />
      </div>
    );
  }

  if (tipo.isError || !tipo.data) {
    return (
      <Alert variant="danger" title="No se pudo cargar el tipo documental">
        {extractApiMessage(tipo.error)}
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <Link to="/configuracion" className="text-sm text-brand-700 hover:underline">
        ← Volver a tipos documentales
      </Link>

      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-slate-900">
              {tipo.data.nombre}
            </h1>
            <span
              className={
                tipo.data.estado === "activo"
                  ? "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide text-emerald-800"
                  : "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide text-slate-600"
              }
            >
              {tipo.data.estado === "activo" ? "Activo" : "Inactivo"}
            </span>
          </div>
          {tipo.data.descripcion && (
            <p className="text-sm text-slate-600">{tipo.data.descripcion}</p>
          )}
        </div>
        <Link
          to={`/configuracion/tipos/${tipo.data.id}/versiones/nueva`}
          className="inline-flex items-center gap-2 rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          Nueva version
        </Link>
      </header>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
          Versiones de prompt
        </h2>

        {versiones.isLoading && (
          <div className="flex items-center justify-center py-10 text-slate-500">
            <Spinner size="md" />
          </div>
        )}

        {versiones.isError && (
          <Alert variant="danger" title="No se pudieron cargar las versiones">
            {extractApiMessage(versiones.error)}
          </Alert>
        )}

        {versiones.data && (
          <PromptVersionsTable
            tipoId={tipo.data.id}
            versions={versiones.data}
          />
        )}
      </section>
    </div>
  );
}
