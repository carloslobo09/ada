import { apiClient } from "@/lib/apiClient";
import type {
  CreateUserInput,
  ResetPasswordInput,
  UpdateUserInput,
  Usuario,
} from "@/features/users/types";

export async function listUsers(): Promise<Usuario[]> {
  const response = await apiClient.get<Usuario[]>("/users");
  return response.data;
}

export async function createUser(payload: CreateUserInput): Promise<Usuario> {
  const response = await apiClient.post<Usuario>("/users", payload);
  return response.data;
}

export async function updateUser(
  userId: string,
  payload: UpdateUserInput,
): Promise<Usuario> {
  const response = await apiClient.patch<Usuario>(`/users/${userId}`, payload);
  return response.data;
}

export async function resetPassword(
  userId: string,
  payload: ResetPasswordInput,
): Promise<Usuario> {
  const response = await apiClient.post<Usuario>(
    `/users/${userId}/reset-password`,
    payload,
  );
  return response.data;
}
