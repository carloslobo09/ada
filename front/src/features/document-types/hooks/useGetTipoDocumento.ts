import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/apiClient";
import type { TipoDocumento } from "@/features/document-types/types";

async function getTipoDocumento(tipoId: string): Promise<TipoDocumento> {
  const response = await apiClient.get<TipoDocumento>(`/document-types/${tipoId}`);
  return response.data;
}

export function useGetTipoDocumento(tipoId: string | undefined) {
  return useQuery({
    queryKey: ["document-types", tipoId],
    queryFn: () => getTipoDocumento(tipoId as string),
    enabled: Boolean(tipoId),
  });
}
