export type EstadoTipoDocumento = "activo" | "inactivo";

export interface TipoDocumento {
  id: string;
  nombre: string;
  slug: string;
  descripcion: string | null;
  estado: EstadoTipoDocumento;
  created_at: string;
}

export interface CreateTipoDocumentoInput {
  nombre: string;
  descripcion: string | null;
}

export interface UpdateTipoDocumentoInput {
  nombre?: string;
  descripcion?: string | null;
  estado?: EstadoTipoDocumento;
}
