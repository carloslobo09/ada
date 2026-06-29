import { useMutation } from "@tanstack/react-query";
import { simulatePromptVersion } from "@/features/prompts/api/promptsClient";

export function useSimulatePromptVersion() {
  return useMutation({
    mutationFn: simulatePromptVersion,
  });
}
