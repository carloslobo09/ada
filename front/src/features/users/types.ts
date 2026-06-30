import type { Rol } from "@/features/auth/types";

export type EstadoUsuario = "activo" | "inactivo";

export interface Usuario {
  id: string;
  email: string;
  nombre: string;
  rol: Rol;
  estado: EstadoUsuario;
  fecha_alta: string;
}

export interface CreateUserInput {
  email: string;
  nombre: string;
  rol: Rol;
  password: string;
}

export interface UpdateUserInput {
  nombre?: string;
  rol?: Rol;
  estado?: EstadoUsuario;
}

export interface ResetPasswordInput {
  new_password: string;
}
