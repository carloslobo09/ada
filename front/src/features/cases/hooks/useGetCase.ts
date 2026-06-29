import { useQuery } from "@tanstack/react-query";
import { getCase } from "@/features/cases/api/casesClient";

export function useGetCase(caseId: string | undefined) {
  return useQuery({
    queryKey: ["cases", caseId],
    queryFn: () => getCase(caseId as string),
    enabled: Boolean(caseId),
  });
}
