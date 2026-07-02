import type { EstadoUsuario, Rol, Usuario } from "@/features/auth/types";

export type { EstadoUsuario, Usuario };

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
