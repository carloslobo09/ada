import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deletePromptVersion } from "@/features/prompts/api/promptsClient";

export function useDeletePromptVersion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deletePromptVersion,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prompt-versions"] });
    },
  });
}
