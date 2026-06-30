import { useState, type ReactNode } from "react";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import { Spinner } from "@/components/Spinner";
import { useConfirm } from "@/contexts/ConfirmContext";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { ResetPasswordDialog } from "@/features/users/components/ResetPasswordDialog";
import { UserForm } from "@/features/users/components/UserForm";
import { UsersTable } from "@/features/users/components/UsersTable";
import { useCreateUser } from "@/features/users/hooks/useCreateUser";
import { useListUsers } from "@/features/users/hooks/useListUsers";
import { useResetPassword } from "@/features/users/hooks/useResetPassword";
import { useUpdateUser } from "@/features/users/hooks/useUpdateUser";
import type {
  CreateUserInput,
  UpdateUserInput,
  Usuario,
} from "@/features/users/types";
import { extractApiMessage } from "@/lib/errors";

export function UsersPage(): ReactNode {
  const { user } = useAuth();
  const confirm = useConfirm();

  const list = useListUsers();
  const create = useCreateUser();
  const update = useUpdateUser();
  const reset = useResetPassword();

  const [editing, setEditing] = useState<Usuario | null>(null);
  const [showCreate, setShowCreate] = useState<boolean>(false);
  const [resetting, setResetting] = useState<Usuario | null>(null);

  function handleCreate(payload: CreateUserInput): void {
    create.mutate(payload, { onSuccess: () => setShowCreate(false) });
  }

  function handleUpdate(payload: UpdateUserInput): void {
    if (!editing) return;
    update.mutate(
      { userId: editing.id, payload },
      { onSuccess: () => setEditing(null) },
    );
  }

  async function handleToggleEstado(usuario: Usuario): Promise<void> {
    const next = usuario.estado === "activo" ? "inactivo" : "activo";
    const verbo = usuario.estado === "activo" ? "desactivar" : "activar";
    const ok = await confirm({
      title: `Confirmar ${verbo}`,
      message: `Vas a ${verbo} a "${usuario.nombre}". Si lo desactivas, no podra iniciar sesion hasta que lo reactives.`,
      confirmLabel: verbo.charAt(0).toUpperCase() + verbo.slice(1),
      variant: usuario.estado === "activo" ? "danger" : "primary",
    });
    if (!ok) return;
    update.mutate({ userId: usuario.id, payload: { estado: next } });
  }

  function handleResetConfirm(newPassword: string): void {
    if (!resetting) return;
    reset.mutate(
      { userId: resetting.id, newPassword },
      { onSuccess: () => setResetting(null) },
    );
  }

  const busyId =
    update.isPending || reset.isPending
      ? (update.variables?.userId ?? reset.variables?.userId ?? null)
      : null;

  return (
    <div className="space-y-6">
      <header className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold text-slate-900">Usuarios</h1>
          <p className="text-sm text-slate-600">
            Gestiona las cuentas operativas de la plataforma: clientes, entrenadores y
            administradores.
          </p>
        </div>
        {!showCreate && (
          <Button onClick={() => setShowCreate(true)}>Nuevo usuario</Button>
        )}
      </header>

      {showCreate && (
        <UserForm
          submitting={create.isPending}
          errorMessage={create.error ? extractApiMessage(create.error) : null}
          onSubmitCreate={handleCreate}
          onCancel={() => setShowCreate(false)}
        />
      )}

      {editing && (
        <UserForm
          initial={editing}
          submitting={update.isPending}
          errorMessage={update.error ? extractApiMessage(update.error) : null}
          onSubmitUpdate={handleUpdate}
          onCancel={() => setEditing(null)}
        />
      )}

      {list.isLoading && (
        <div className="flex items-center justify-center py-20 text-slate-500">
          <Spinner size="lg" />
        </div>
      )}

      {list.isError && (
        <Alert variant="danger" title="No se pudieron cargar los usuarios">
          {list.error instanceof Error ? list.error.message : "Error desconocido."}
        </Alert>
      )}

      {list.data && user && (
        <UsersTable
          usuarios={list.data}
          currentUserId={user.id}
          onEdit={setEditing}
          onToggleEstado={handleToggleEstado}
          onResetPassword={setResetting}
          busyId={busyId}
        />
      )}

      <ResetPasswordDialog
        open={Boolean(resetting)}
        usuarioNombre={resetting?.nombre ?? ""}
        submitting={reset.isPending}
        errorMessage={reset.error ? extractApiMessage(reset.error) : null}
        onConfirm={handleResetConfirm}
        onCancel={() => setResetting(null)}
      />
    </div>
  );
}
