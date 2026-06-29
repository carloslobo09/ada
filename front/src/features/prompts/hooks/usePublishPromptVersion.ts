import { useMutation, useQueryClient } from "@tanstack/react-query";
import { publishPromptVersion } from "@/features/prompts/api/promptsClient";

export function usePublishPromptVersion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: publishPromptVersion,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prompt-versions"] });
    },
  });
}
