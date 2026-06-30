import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/Button";
import type { TipoDocumento } from "@/features/document-types/types";

interface TiposDocumentoTableProps {
  tipos: TipoDocumento[];
  isAdmin: boolean;
  onEdit: (tipo: TipoDocumento) => void;
  onToggleEstado: (tipo: TipoDocumento) => void;
  onDelete: (tipo: TipoDocumento) => void;
  busyId?: string | null;
}

export function TiposDocumentoTable({
  tipos,
  isAdmin,
  onEdit,
  onToggleEstado,
  onDelete,
  busyId,
}: TiposDocumentoTableProps): ReactNode {
  const navigate = useNavigate();

  if (tipos.length === 0) {
    return <p className="text-sm text-slate-500">Sin tipos documentales cargados.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-2 text-left font-semibold">Nombre</th>
            <th className="px-4 py-2 text-left font-semibold">Descripcion</th>
            <th className="px-4 py-2 text-left font-semibold">Estado</th>
            <th className="px-4 py-2 text-right font-semibold">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {tipos.map((tipo) => {
            const isBusy = busyId === tipo.id;
            const activo = tipo.estado === "activo";
            return (
              <tr key={tipo.id} className="hover:bg-slate-50">
                <td className="px-4 py-2 font-medium text-slate-800">{tipo.nombre}</td>
                <td className="px-4 py-2 text-slate-600">
                  {tipo.descripcion ?? <span className="text-slate-400">-</span>}
                </td>
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
                      size="sm"
                      onClick={() => navigate(`/configuracion/tipos/${tipo.id}`)}
                      disabled={isBusy}
                    >
                      Ver versiones
                    </Button>
                    {isAdmin && (
                      <>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => onEdit(tipo)}
                          disabled={isBusy}
                        >
                          Editar
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => onToggleEstado(tipo)}
                          disabled={isBusy}
                        >
                          {activo ? "Desactivar" : "Activar"}
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => onDelete(tipo)}
                          disabled={isBusy}
                        >
                          Eliminar
                        </Button>
                      </>
                    )}
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
