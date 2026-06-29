import { apiClient } from "@/lib/apiClient";
import type { LoginRequest, LoginResponse, Usuario } from "@/features/auth/types";

export async function login(payload: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>("/auth/login", payload);
  return response.data;
}

export async function fetchMe(): Promise<Usuario> {
  const response = await apiClient.get<Usuario>("/auth/me");
  return response.data;
}
