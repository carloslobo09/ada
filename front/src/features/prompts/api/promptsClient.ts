import { apiClient } from "@/lib/apiClient";
import type {
  CreatePromptVersionInput,
  PromptVersion,
  PromptVersionListItem,
  SimulationInput,
  SimulationResult,
} from "@/features/prompts/types";

export async function listPromptVersions(
  tipoDocumentoId?: string,
): Promise<PromptVersionListItem[]> {
  const response = await apiClient.get<PromptVersionListItem[]>("/prompt-versions", {
    params: tipoDocumentoId ? { tipo_documento_id: tipoDocumentoId } : undefined,
  });
  return response.data;
}

export async function getPromptVersion(versionId: string): Promise<PromptVersion> {
  const response = await apiClient.get<PromptVersion>(`/prompt-versions/${versionId}`);
  return response.data;
}

export async function createPromptVersion(
  payload: CreatePromptVersionInput,
): Promise<PromptVersion> {
  const response = await apiClient.post<PromptVersion>("/prompt-versions", payload);
  return response.data;
}

export async function publishPromptVersion(versionId: string): Promise<PromptVersion> {
  const response = await apiClient.patch<PromptVersion>(
    `/prompt-versions/${versionId}/publish`,
  );
  return response.data;
}

export async function deletePromptVersion(versionId: string): Promise<void> {
  await apiClient.delete(`/prompt-versions/${versionId}`);
}

export async function simulatePromptVersion(input: SimulationInput): Promise<SimulationResult> {
  const form = new FormData();
  form.append("file", input.file);
  if (input.expected && Object.keys(input.expected).length > 0) {
    form.append("expected", JSON.stringify(input.expected));
  }
  const response = await apiClient.post<SimulationResult>(
    `/prompt-versions/${input.versionId}/simulate`,
    form,
  );
  return response.data;
}
