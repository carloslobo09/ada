import { createContext, useCallback, useEffect, useState, type ReactNode } from "react";
import { fetchMe, login as loginRequest } from "@/features/auth/api/authClient";
import type { LoginRequest, Usuario } from "@/features/auth/types";
import { clearToken, readToken, storeToken } from "@/lib/apiClient";

interface AuthContextValue {
  user: Usuario | null;
  loading: boolean;
  login: (input: LoginRequest) => Promise<Usuario>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps): ReactNode {
  const [user, setUser] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const token = readToken();
    if (!token) {
      setLoading(false);
      return;
    }
    fetchMe()
      .then((fetched) => setUser(fetched))
      .catch(() => {
        clearToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (input: LoginRequest): Promise<Usuario> => {
    const response = await loginRequest(input);
    storeToken(response.access_token);
    setUser(response.user);
    return response.user;
  }, []);

  const logout = useCallback((): void => {
    clearToken();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
