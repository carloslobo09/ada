from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.caso import Caso
from app.schemas.decision import DecisionOut
from app.schemas.documento import DocumentoOut

EstadoRecontrol = Literal["pendiente", "correcto", "incorrecto"]


class CasoOut(BaseModel):
    """Vista completa para entrenador o admin: trazabilidad y refs internas para auditoria."""

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


# --- Vistas para rol cliente ---


class CrossValidationResultCliente(BaseModel):
    """Resultado de una validacion cruzada en formato consumible para el cliente."""

    field: str
    expected: str
    extracted: str
    passed: bool
    reason: str


class DocumentoCliente(BaseModel):
    nombre_archivo: str
    content_type: str
    file_size: int
    fecha_recepcion: datetime


class CasoClienteOut(BaseModel):
    """Vista resumida del caso, pensada para el sistema integrador.

    Devuelve solo la decision final y sus explicaciones, sin trazabilidad interna
    (ids, hashes, evidencias del LLM ni estado de Re Control).
    """

    id: str
    fecha_creacion: datetime
    estado: str

    veredicto: str | None
    motivos: str | None

    campos_extraidos: dict[str, Any] | None
    validaciones_cruzadas: list[CrossValidationResultCliente] | None

    documento: DocumentoCliente | None


class CasoClienteListItem(BaseModel):
    id: str
    fecha_creacion: datetime
    estado: str
    veredicto: str | None


class CasoClienteListOut(BaseModel):
    items: list[CasoClienteListItem]
    limit: int
    offset: int


def to_cliente_out(caso: Caso) -> CasoClienteOut:
    decision = caso.decision
    refs = decision.refs_evidencias if decision else None

    campos = None
    if refs and isinstance(refs.get("resultado_extraccion"), dict):
        campos = refs["resultado_extraccion"].get("campos_normalizados")

    cross = None
    if decision and decision.cross_validation_results:
        cross = [
            CrossValidationResultCliente(
                field=item["field"],
                expected=item["expected"],
                extracted=item["extracted"],
                passed=item["passed"],
                reason=item["reason"],
            )
            for item in decision.cross_validation_results
        ]

    documento_cliente = None
    if caso.documento is not None:
        documento_cliente = DocumentoCliente(
            nombre_archivo=caso.documento.nombre_original,
            content_type=caso.documento.content_type,
            file_size=caso.documento.file_size,
            fecha_recepcion=caso.documento.fecha_recepcion,
        )

    return CasoClienteOut(
        id=caso.id,
        fecha_creacion=caso.fecha_creacion,
        estado=caso.estado,
        veredicto=decision.veredicto if decision else None,
        motivos=decision.motivos if decision else None,
        campos_extraidos=campos,
        validaciones_cruzadas=cross,
        documento=documento_cliente,
    )


def to_cliente_list_item(caso: Caso) -> CasoClienteListItem:
    return CasoClienteListItem(
        id=caso.id,
        fecha_creacion=caso.fecha_creacion,
        estado=caso.estado,
        veredicto=caso.decision.veredicto if caso.decision else None,
    )
