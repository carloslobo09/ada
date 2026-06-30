from pathlib import Path
from typing import Any

from app.schemas.extraction import FieldExtractionSchema
from app.services.extraction.protocol import DniExtractionResult, Extractor

_SMART_VALUES: dict[str, dict[str, Any]] = {
    "numero_dni": {"value": "40123456", "confidence": 0.98},
    "nombre_completo": {"value": "LOBO CARLOS IGNACIO", "confidence": 0.96},
    "fecha_nacimiento": {"value": "1997-08-15", "confidence": 0.97},
    "fecha_emision": {"value": "2018-05-20", "confidence": 0.95},
    "fecha_vencimiento": {"value": "2033-05-20", "confidence": 0.96},
    "sexo": {"value": "M", "confidence": 0.99},
    "nacionalidad": {"value": "ARGENTINA", "confidence": 0.99},
    "lugar_nacimiento": {"value": "BUENOS AIRES", "confidence": 0.94},
    "numero_tramite": {"value": "00123456789", "confidence": 0.93},
    "tipo_documento": {
        "value": "Registro Nacional de las Personas",
        "confidence": 1.0,
    },
    "domicilio": {
        "value": "AV. RIVADAVIA 1234, CIUDAD AUTONOMA DE BUENOS AIRES",
        "confidence": 0.92,
    },
    "dorso_presente": {"value": "SI", "confidence": 0.95},
}


class MockExtractor(Extractor):
    """Genera una respuesta deterministica basada en los campos configurados.

    Para los campos conocidos del DNI usa valores fijos pensados para el demo.
    Para los desconocidos (nuevos campos definidos por el usuario en una version
    de prompt) responde con un placeholder y confianza media.
    """

    def __init__(self, extraction_fields: list[dict[str, Any]]) -> None:
        self._extraction_fields = extraction_fields

    def extract(self, file_path: Path, content_type: str) -> DniExtractionResult:
        payload: dict[str, dict[str, Any]] = {}
        for cfg in self._extraction_fields:
            name = cfg["name"]
            smart = _SMART_VALUES.get(name)
            if smart is not None:
                payload[name] = {
                    "value": smart["value"],
                    "confidence": smart["confidence"],
                    "status": "approved",
                }
            else:
                payload[name] = {
                    "value": f"MOCK_{name.upper()}",
                    "confidence": 0.85,
                    "status": "approved",
                }
        fields = {
            name: FieldExtractionSchema.model_validate(item)
            for name, item in payload.items()
        }
        return DniExtractionResult(fields=fields, raw_response=payload)
