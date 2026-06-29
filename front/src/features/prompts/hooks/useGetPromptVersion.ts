import { useQuery } from "@tanstack/react-query";
import { getPromptVersion } from "@/features/prompts/api/promptsClient";

export function useGetPromptVersion(versionId: string | undefined) {
  return useQuery({
    queryKey: ["prompt-versions", versionId],
    queryFn: () => getPromptVersion(versionId as string),
    enabled: Boolean(versionId),
  });
}
