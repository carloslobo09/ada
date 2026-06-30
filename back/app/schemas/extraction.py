from typing import Any, Literal

from pydantic import BaseModel, Field

FieldStatus = Literal["approved", "rejected"]


class FieldExtractionSchema(BaseModel):
    """Resultado de extraer un unico campo con su confianza y estado."""

    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    status: FieldStatus


def build_response_schema(extraction_fields: list[dict[str, Any]]) -> dict[str, Any]:
    """Construye dinamicamente el JSON Schema esperado de la respuesta del modelo.

    A partir de la lista de campos configurada en la version del prompt, arma el
    schema que se pasa como `response_schema` al adaptador LLM. Esto desacopla al
    extractor de un tipo documental especifico.
    """
    field_names = [item["name"] for item in extraction_fields]
    return {
        "type": "object",
        "properties": {
            name: {
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
            for name in field_names
        },
        "required": field_names,
    }
