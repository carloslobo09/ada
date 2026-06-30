import { useQuery } from "@tanstack/react-query";
import { getCase, getCaseCliente } from "@/features/cases/api/casesClient";

export function useGetCase(caseId: string | undefined) {
  return useQuery({
    queryKey: ["cases", caseId],
    queryFn: () => getCase(caseId as string),
    enabled: Boolean(caseId),
  });
}

export function useGetCaseCliente(caseId: string | undefined) {
  return useQuery({
    queryKey: ["cases", "cliente", caseId],
    queryFn: () => getCaseCliente(caseId as string),
    enabled: Boolean(caseId),
  });
}
