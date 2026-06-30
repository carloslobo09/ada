import { useQuery } from "@tanstack/react-query";
import { listTiposDocumento } from "@/features/document-types/api/tiposClient";

export function useListTiposDocumento(soloActivos = false) {
  return useQuery({
    queryKey: ["document-types", { soloActivos }],
    queryFn: () => listTiposDocumento(soloActivos),
  });
}
