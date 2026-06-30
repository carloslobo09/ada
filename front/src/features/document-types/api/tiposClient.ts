import { apiClient } from "@/lib/apiClient";
import type {
  CreateTipoDocumentoInput,
  TipoDocumento,
  UpdateTipoDocumentoInput,
} from "@/features/document-types/types";

export async function listTiposDocumento(
  soloActivos = false,
): Promise<TipoDocumento[]> {
  const response = await apiClient.get<TipoDocumento[]>("/document-types", {
    params: { solo_activos: soloActivos },
  });
  return response.data;
}

export async function createTipoDocumento(
  payload: CreateTipoDocumentoInput,
): Promise<TipoDocumento> {
  const response = await apiClient.post<TipoDocumento>("/document-types", payload);
  return response.data;
}

export async function updateTipoDocumento(
  tipoId: string,
  payload: UpdateTipoDocumentoInput,
): Promise<TipoDocumento> {
  const response = await apiClient.patch<TipoDocumento>(
    `/document-types/${tipoId}`,
    payload,
  );
  return response.data;
}

export async function deleteTipoDocumento(tipoId: string): Promise<void> {
  await apiClient.delete(`/document-types/${tipoId}`);
}
