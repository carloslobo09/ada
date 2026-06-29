import type { ReactNode } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import { Spinner } from "@/components/Spinner";
import { ActiveBadge } from "@/features/prompts/components/ActiveBadge";
import { CrossFieldsEditor } from "@/features/prompts/components/CrossFieldsEditor";
import { SimulationPanel } from "@/features/prompts/components/SimulationPanel";
import { useDeletePromptVersion } from "@/features/prompts/hooks/useDeletePromptVersion";
import { useGetPromptVersion } from "@/features/prompts/hooks/useGetPromptVersion";
import { usePublishPromptVersion } from "@/features/prompts/hooks/usePublishPromptVersion";
import { extractApiMessage } from "@/lib/errors";

export function PromptVersionDetailPage(): ReactNode {
  const { versionId } = useParams<{ versionId: string }>();
  const navigate = useNavigate();
  const { data, isLoading, isError, error } = useGetPromptVersion(versionId);
  const publish = usePublishPromptVersion();
  const remove = useDeletePromptVersion();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-500">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <Alert variant="danger" title="No se pudo cargar la version">
        {error instanceof Error ? error.message : "Version no encontrada."}
      </Alert>
    );
  }

  function handlePublish(): void {
    if (!data) return;
    publish.mutate(data.id);
  }

  function handleDelete(): void {
    if (!data) return;
    if (!window.confirm(`Eliminar la version v${data.numero}? Esta accion no se puede deshacer.`)) {
      return;
    }
    remove.mutate(data.id, {
      onSuccess: () => navigate("/configuracion"),
    });
  }

  const esPublicada = data.estado === "publicada";
  const esBorrador = data.estado === "borrador";

  return (
    <div className="space-y-6">
      <Link to="/configuracion" className="text-sm text-brand-700 hover:underline">
        ← Volver a configuracion
      </Link>

      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-slate-900">Version v{data.numero}</h1>
            <ActiveBadge estado={data.estado} />
          </div>
          <p className="text-sm text-slate-600">
            Creada {new Date(data.created_at).toLocaleString("es-AR")}
            {data.activated_at &&
              ` - Publicada ${new Date(data.activated_at).toLocaleString("es-AR")}`}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            to={`/configuracion/nueva?base=${data.id}`}
            className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Duplicar a nueva version
          </Link>
          {esBorrador && (
            <Button onClick={handlePublish} loading={publish.isPending}>
              Publicar
            </Button>
          )}
          {!esPublicada && (
            <Button variant="secondary" onClick={handleDelete} loading={remove.isPending}>
              Eliminar
            </Button>
          )}
        </div>
      </header>

      {publish.error && (
        <Alert variant="danger" title="No se pudo publicar">
          {extractApiMessage(publish.error)}
        </Alert>
      )}
      {remove.error && (
        <Alert variant="danger" title="No se pudo eliminar">
          {extractApiMessage(remove.error)}
        </Alert>
      )}

      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">Prompt</h2>
        <pre className="overflow-x-auto rounded-md border border-slate-200 bg-white p-4 font-mono text-xs text-slate-800 whitespace-pre-wrap">
          {data.prompt_text}
        </pre>
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
          Validacion cruzada
        </h2>
        <CrossFieldsEditor value={data.cross_validation_config} onChange={() => {}} readOnly />
      </section>

      <SimulationPanel versionId={data.id} crossFields={data.cross_validation_config} />
    </div>
  );
}
