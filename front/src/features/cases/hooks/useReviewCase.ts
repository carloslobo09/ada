import { useMutation, useQueryClient } from "@tanstack/react-query";
import { reviewCase } from "@/features/cases/api/casesClient";
import type { ReviewInput } from "@/features/cases/types";

interface Vars {
  caseId: string;
  input: ReviewInput;
}

export function useReviewCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ caseId, input }: Vars) => reviewCase(caseId, input),
    onSuccess: (caso) => {
      queryClient.invalidateQueries({ queryKey: ["cases"] });
      queryClient.setQueryData(["cases", caso.id], caso);
    },
  });
}
