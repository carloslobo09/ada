from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.decision import DecisionOut
from app.schemas.documento import DocumentoOut

EstadoRecontrol = Literal["pendiente", "correcto", "incorrecto"]


class CasoOut(BaseModel):
    """Vista completa de un caso: refs a Documento y Decision, mas campos del Re Control."""

    id: str
    fecha_creacion: datetime
    estado: str

    ref_documento: str | None
    ref_decision: str | None
    ref_usuario_cliente: str | None

    documento: DocumentoOut | None
    decision: DecisionOut | None

    estado_recontrol: EstadoRecontrol
    observacion_recontrol: str | None
    ref_usuario_recontrol: str | None
    fecha_recontrol: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CasoListItem(BaseModel):
    id: str
    fecha_creacion: datetime
    estado: str
    estado_recontrol: EstadoRecontrol
    decision: DecisionOut | None

    model_config = ConfigDict(from_attributes=True)


class CasoListOut(BaseModel):
    items: list[CasoListItem]
    limit: int
    offset: int


class ReviewRequest(BaseModel):
    estado_recontrol: EstadoRecontrol
    observacion_recontrol: str | None = Field(default=None, max_length=2048)
