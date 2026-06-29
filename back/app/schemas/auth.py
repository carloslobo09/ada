from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Rol = Literal["cliente", "entrenador", "admin"]


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=255)


class UsuarioOut(BaseModel):
    id: str
    email: str
    nombre: str
    rol: Rol
    estado: str
    fecha_alta: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UsuarioOut


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
