import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ActiveBadge } from "@/features/prompts/components/ActiveBadge";
import type { PromptVersionListItem } from "@/features/prompts/types";

interface PromptVersionsTableProps {
  versions: PromptVersionListItem[];
}

export function PromptVersionsTable({ versions }: PromptVersionsTableProps): ReactNode {
  if (versions.length === 0) {
    return <p className="text-sm text-slate-500">Sin versiones disponibles.</p>;
  }
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-2 text-left font-semibold">Numero</th>
            <th className="px-4 py-2 text-left font-semibold">Creada</th>
            <th className="px-4 py-2 text-left font-semibold">Publicada</th>
            <th className="px-4 py-2 text-left font-semibold">Estado</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {versions.map((version) => (
            <tr key={version.id} className="hover:bg-slate-50">
              <td className="px-4 py-2">
                <Link
                  to={`/configuracion/${version.id}`}
                  className="font-medium text-brand-700 hover:underline"
                >
                  v{version.numero}
                </Link>
              </td>
              <td className="px-4 py-2 text-slate-500">
                {new Date(version.created_at).toLocaleString("es-AR")}
              </td>
              <td className="px-4 py-2 text-slate-500">
                {version.activated_at
                  ? new Date(version.activated_at).toLocaleString("es-AR")
                  : "-"}
              </td>
              <td className="px-4 py-2">
                <ActiveBadge estado={version.estado} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
