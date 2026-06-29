import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createPromptVersion } from "@/features/prompts/api/promptsClient";

export function useCreatePromptVersion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createPromptVersion,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prompt-versions"] });
    },
  });
}
