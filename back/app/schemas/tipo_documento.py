from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EstadoTipoDocumento = Literal["activo", "inactivo"]


class TipoDocumentoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str | None = Field(default=None, max_length=1024)


class TipoDocumentoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    descripcion: str | None = Field(default=None, max_length=1024)
    estado: EstadoTipoDocumento | None = None


class TipoDocumentoOut(BaseModel):
    id: str
    nombre: str
    descripcion: str | None
    estado: EstadoTipoDocumento
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
