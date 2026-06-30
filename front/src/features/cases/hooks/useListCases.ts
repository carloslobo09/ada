import { useQuery } from "@tanstack/react-query";
import {
  listCases,
  listCasesCliente,
  type ListCasesParams,
} from "@/features/cases/api/casesClient";

export function useListCases(params: ListCasesParams = {}) {
  return useQuery({
    queryKey: ["cases", params],
    queryFn: () => listCases(params),
  });
}

export function useListCasesCliente() {
  return useQuery({
    queryKey: ["cases", "cliente"],
    queryFn: listCasesCliente,
  });
}
