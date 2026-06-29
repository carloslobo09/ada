import { useQuery } from "@tanstack/react-query";
import { listCases, type ListCasesParams } from "@/features/cases/api/casesClient";

export function useListCases(params: ListCasesParams = {}) {
  return useQuery({
    queryKey: ["cases", params],
    queryFn: () => listCases(params),
  });
}
