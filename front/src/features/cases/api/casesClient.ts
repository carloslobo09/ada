import { apiClient } from "@/lib/apiClient";
import type {
  Case,
  CasesPage,
  EstadoRecontrol,
  ReviewInput,
} from "@/features/cases/types";

export async function getCase(caseId: string): Promise<Case> {
  const response = await apiClient.get<Case>(`/cases/${caseId}`);
  return response.data;
}

export interface ListCasesParams {
  limit?: number;
  offset?: number;
  recontrol?: EstadoRecontrol;
}

export async function listCases(params: ListCasesParams = {}): Promise<CasesPage> {
  const { limit = 50, offset = 0, recontrol } = params;
  const response = await apiClient.get<CasesPage>("/cases", {
    params: { limit, offset, ...(recontrol ? { recontrol } : {}) },
  });
  return response.data;
}

export async function reviewCase(caseId: string, input: ReviewInput): Promise<Case> {
  const response = await apiClient.patch<Case>(`/cases/${caseId}/review`, input);
  return response.data;
}
