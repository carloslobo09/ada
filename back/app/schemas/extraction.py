from typing import Literal

from pydantic import BaseModel, Field

FieldStatus = Literal["approved", "rejected"]

DNI_FIELDS: tuple[str, ...] = (
    "numero_dni",
    "nombre_completo",
    "fecha_nacimiento",
    "fecha_emision",
    "fecha_vencimiento",
    "sexo",
    "nacionalidad",
    "lugar_nacimiento",
    "numero_tramite",
    "tipo_documento",
    "domicilio",
    "dorso_presente",
)


class FieldExtractionSchema(BaseModel):
    """Resultado de extraer un unico campo con su confianza y estado."""

    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    status: FieldStatus


class DniExtractionSchema(BaseModel):
    """Contrato de salida del modelo para el DNI argentino."""

    numero_dni: FieldExtractionSchema
    nombre_completo: FieldExtractionSchema
    fecha_nacimiento: FieldExtractionSchema
    fecha_emision: FieldExtractionSchema
    fecha_vencimiento: FieldExtractionSchema
    sexo: FieldExtractionSchema
    nacionalidad: FieldExtractionSchema
    lugar_nacimiento: FieldExtractionSchema
    numero_tramite: FieldExtractionSchema
    tipo_documento: FieldExtractionSchema
    domicilio: FieldExtractionSchema
    dorso_presente: FieldExtractionSchema


DNI_RESPONSE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        campo: {
            "type": "object",
            "properties": {
                "value": {"type": "string"},
                "confidence": {"type": "number"},
                "status": {
                    "type": "string",
                    "enum": ["approved", "rejected"],
                },
            },
            "required": ["value", "confidence", "status"],
        }
        for campo in DNI_FIELDS
    },
    "required": list(DNI_FIELDS),
}
