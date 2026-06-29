import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "ada.token";

export const apiClient = axios.create({
  baseURL,
  headers: { Accept: "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      const onLogin = window.location.pathname === "/login";
      if (!onLogin) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

export function storeToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function readToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}
