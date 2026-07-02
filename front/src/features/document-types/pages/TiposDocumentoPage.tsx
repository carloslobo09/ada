import { useState, type ReactNode } from "react";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import { Spinner } from "@/components/Spinner";
import { TipoDocumentoForm } from "@/features/document-types/components/TipoDocumentoForm";
import { TiposDocumentoTable } from "@/features/document-types/components/TiposDocumentoTable";
import { useCreateTipoDocumento } from "@/features/document-types/hooks/useCreateTipoDocumento";
import { useDeleteTipoDocumento } from "@/features/document-types/hooks/useDeleteTipoDocumento";
import { useListTiposDocumento } from "@/features/document-types/hooks/useListTiposDocumento";
import { useUpdateTipoDocumento } from "@/features/document-types/hooks/useUpdateTipoDocumento";
import type {
  CreateTipoDocumentoInput,
  TipoDocumento,
} from "@/features/document-types/types";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { useConfirm } from "@/contexts/ConfirmContext";
import { extractApiMessage } from "@/lib/errors";

export function TiposDocumentoPage(): ReactNode {
  const { user } = useAuth();
  const confirm = useConfirm();
  const isAdmin = user?.rol === "admin";

  const list = useListTiposDocumento();
  const create = useCreateTipoDocumento();
  const update = useUpdateTipoDocumento();
  const remove = useDeleteTipoDocumento();

  const [editing, setEditing] = useState<TipoDocumento | null>(null);
  const [showCreate, setShowCreate] = useState<boolean>(false);

  function openCreate(): void {
    create.reset();
    setShowCreate(true);
  }

  function openEdit(tipo: TipoDocumento): void {
    update.reset();
    setEditing(tipo);
  }

  function handleCreate(payload: CreateTipoDocumentoInput): void {
    create.mutate(payload, {
      onSuccess: () => {
        setShowCreate(false);
      },
    });
  }

  function handleUpdate(payload: CreateTipoDocumentoInput): void {
    if (!editing) return;
    update.mutate(
      { tipoId: editing.id, payload },
      { onSuccess: () => setEditing(null) },
    );
  }

  async function handleToggleEstado(tipo: TipoDocumento): Promise<void> {
    const next = tipo.estado === "activo" ? "inactivo" : "activo";
    const verbo = tipo.estado === "activo" ? "desactivar" : "activar";
    const ok = await confirm({
      title: `Confirmar ${verbo}`,
      message: `Vas a ${verbo} el tipo "${tipo.nombre}". Podes revertirlo en cualquier momento.`,
      confirmLabel: verbo.charAt(0).toUpperCase() + verbo.slice(1),
      variant: "primary",
    });
    if (!ok) return;
    update.mutate({ tipoId: tipo.id, payload: { estado: next } });
  }

  async function handleDelete(tipo: TipoDocumento): Promise<void> {
    const ok = await confirm({
      title: "Eliminar tipo documental",
      message: `Vas a eliminar "${tipo.nombre}". Si tiene versiones o casos asociados la operacion fallara.`,
      confirmLabel: "Eliminar",
      variant: "danger",
    });
    if (!ok) return;
    remove.mutate(tipo.id);
  }

  const busyId =
    update.isPending || remove.isPending
      ? (update.variables?.tipoId ?? remove.variables ?? null)
      : null;

  return (
    <div className="space-y-6">
      <header className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold text-slate-900">Configuracion</h1>
          <p className="text-sm text-slate-600">
            Tipos documentales que el sistema puede procesar. Entra a cada tipo para
            gestionar sus versiones de prompt y reglas de validacion cruzada.
          </p>
        </div>
        {isAdmin && !showCreate && (
          <Button onClick={openCreate}>Nuevo tipo</Button>
        )}
      </header>

      {isAdmin && showCreate && (
        <TipoDocumentoForm
          submitting={create.isPending}
          errorMessage={create.error ? extractApiMessage(create.error) : null}
          onSubmit={handleCreate}
          onCancel={() => setShowCreate(false)}
          submitLabel="Crear tipo"
        />
      )}

      {isAdmin && editing && (
        <TipoDocumentoForm
          initial={editing}
          submitting={update.isPending}
          errorMessage={update.error ? extractApiMessage(update.error) : null}
          onSubmit={handleUpdate}
          onCancel={() => setEditing(null)}
          submitLabel="Guardar cambios"
        />
      )}

      {remove.error && (
        <Alert variant="danger" title="No se pudo eliminar">
          {extractApiMessage(remove.error)}
        </Alert>
      )}

      {update.error && !editing && (
        <Alert variant="danger" title="No se pudo actualizar el estado">
          {extractApiMessage(update.error)}
        </Alert>
      )}

      {list.isLoading && (
        <div className="flex items-center justify-center py-20 text-slate-500">
          <Spinner size="lg" />
        </div>
      )}

      {list.isError && (
        <Alert variant="danger" title="No se pudieron cargar los tipos documentales">
          {extractApiMessage(list.error)}
        </Alert>
      )}

      {list.data && (
        <TiposDocumentoTable
          tipos={list.data}
          isAdmin={isAdmin}
          onEdit={openEdit}
          onToggleEstado={handleToggleEstado}
          onDelete={handleDelete}
          busyId={busyId}
        />
      )}
    </div>
  );
}
