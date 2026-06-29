export type Rol = "cliente" | "entrenador" | "admin";

export interface Usuario {
  id: string;
  email: string;
  nombre: string;
  rol: Rol;
  estado: string;
  fecha_alta: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  user: Usuario;
}
