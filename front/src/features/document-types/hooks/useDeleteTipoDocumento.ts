import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteTipoDocumento } from "@/features/document-types/api/tiposClient";

export function useDeleteTipoDocumento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteTipoDocumento,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["document-types"] });
    },
  });
}
