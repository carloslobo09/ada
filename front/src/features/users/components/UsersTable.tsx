import type { ReactNode } from "react";
import { Button } from "@/components/Button";
import { ROL_LABEL } from "@/features/auth/types";
import type { Usuario } from "@/features/users/types";

interface UsersTableProps {
  usuarios: Usuario[];
  currentUserId: string;
  onEdit: (usuario: Usuario) => void;
  onToggleEstado: (usuario: Usuario) => void;
  onResetPassword: (usuario: Usuario) => void;
  busyId?: string | null;
}

export function UsersTable({
  usuarios,
  currentUserId,
  onEdit,
  onToggleEstado,
  onResetPassword,
  busyId,
}: UsersTableProps): ReactNode {
  if (usuarios.length === 0) {
    return <p className="text-sm text-slate-500">Sin usuarios cargados.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-2 text-left font-semibold">Nombre</th>
            <th className="px-4 py-2 text-left font-semibold">Email</th>
            <th className="px-4 py-2 text-left font-semibold">Rol</th>
            <th className="px-4 py-2 text-left font-semibold">Estado</th>
            <th className="px-4 py-2 text-right font-semibold">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {usuarios.map((u) => {
            const isBusy = busyId === u.id;
            const isSelf = u.id === currentUserId;
            const activo = u.estado === "activo";
            return (
              <tr key={u.id} className="hover:bg-slate-50">
                <td className="px-4 py-2 font-medium text-slate-800">
                  {u.nombre}
                  {isSelf && (
                    <span className="ml-2 text-xs font-normal text-slate-500">(vos)</span>
                  )}
                </td>
                <td className="px-4 py-2 text-slate-600">{u.email}</td>
                <td className="px-4 py-2 text-slate-700">{ROL_LABEL[u.rol]}</td>
                <td className="px-4 py-2">
                  <span
                    className={
                      activo
                        ? "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide text-emerald-800"
                        : "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide text-slate-600"
                    }
                  >
                    {activo ? "Activo" : "Inactivo"}
                  </span>
                </td>
                <td className="px-4 py-2">
                  <div className="flex justify-end gap-1.5">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => onEdit(u)}
                      disabled={isBusy || isSelf}
                      title={isSelf ? "No podes editarte a vos mismo" : undefined}
                    >
                      Editar
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => onResetPassword(u)}
                      disabled={isBusy || isSelf}
                      title={isSelf ? "No podes resetear tu propia contrasena" : undefined}
                    >
                      Resetear contrasena
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => onToggleEstado(u)}
                      disabled={isBusy || isSelf}
                      title={isSelf ? "No podes desactivarte a vos mismo" : undefined}
                    >
                      {activo ? "Desactivar" : "Activar"}
                    </Button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
