import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateTipoDocumento } from "@/features/document-types/api/tiposClient";
import type { UpdateTipoDocumentoInput } from "@/features/document-types/types";

interface UpdateInput {
  tipoId: string;
  payload: UpdateTipoDocumentoInput;
}

export function useUpdateTipoDocumento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tipoId, payload }: UpdateInput) =>
      updateTipoDocumento(tipoId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["document-types"] });
    },
  });
}
