from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Rol = Literal["cliente", "entrenador", "admin"]
EstadoUsuario = Literal["activo", "inactivo"]


class UsuarioCreate(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    nombre: str = Field(min_length=1, max_length=120)
    rol: Rol
    password: str = Field(min_length=6, max_length=128)


class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    rol: Rol | None = None
    estado: EstadoUsuario | None = None


class PasswordResetRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)


class UsuarioOut(BaseModel):
    id: str
    email: str
    nombre: str
    rol: Rol
    estado: EstadoUsuario
    fecha_alta: datetime

    model_config = ConfigDict(from_attributes=True)
