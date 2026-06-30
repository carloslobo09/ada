import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createTipoDocumento } from "@/features/document-types/api/tiposClient";

export function useCreateTipoDocumento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createTipoDocumento,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["document-types"] });
    },
  });
}
