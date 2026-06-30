import { useQuery } from "@tanstack/react-query";
import { listPromptVersions } from "@/features/prompts/api/promptsClient";

export function useListPromptVersions(tipoDocumentoId?: string) {
  return useQuery({
    queryKey: ["prompt-versions", { tipoDocumentoId }],
    queryFn: () => listPromptVersions(tipoDocumentoId),
  });
}
