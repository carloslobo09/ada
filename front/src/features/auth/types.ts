export type Rol = "cliente" | "entrenador" | "admin";
export type EstadoUsuario = "activo" | "inactivo";

export const ROL_LABEL: Record<Rol, string> = {
  cliente: "Cliente",
  entrenador: "Entrenador",
  admin: "Administrador",
};

export interface Usuario {
  id: string;
  email: string;
  nombre: string;
  rol: Rol;
  estado: EstadoUsuario;
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
