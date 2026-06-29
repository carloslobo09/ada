import { useQuery } from "@tanstack/react-query";
import { listPromptVersions } from "@/features/prompts/api/promptsClient";

export function useListPromptVersions() {
  return useQuery({
    queryKey: ["prompt-versions"],
    queryFn: listPromptVersions,
  });
}
