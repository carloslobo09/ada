from pathlib import Path

from app.schemas.extraction import FieldExtractionSchema
from app.services.extraction.protocol import DniExtractionResult, Extractor

_MOCK_PAYLOAD: dict[str, dict] = {
    "numero_dni": {"value": "40123456", "confidence": 0.98, "status": "approved"},
    "nombre_completo": {"value": "LOBO CARLOS IGNACIO", "confidence": 0.96, "status": "approved"},
    "fecha_nacimiento": {"value": "1997-08-15", "confidence": 0.97, "status": "approved"},
    "fecha_emision": {"value": "2018-05-20", "confidence": 0.95, "status": "approved"},
    "fecha_vencimiento": {"value": "2033-05-20", "confidence": 0.96, "status": "approved"},
    "sexo": {"value": "M", "confidence": 0.99, "status": "approved"},
    "nacionalidad": {"value": "ARGENTINA", "confidence": 0.99, "status": "approved"},
    "lugar_nacimiento": {"value": "BUENOS AIRES", "confidence": 0.94, "status": "approved"},
    "numero_tramite": {"value": "00123456789", "confidence": 0.93, "status": "approved"},
    "tipo_documento": {
        "value": "Registro Nacional de las Personas",
        "confidence": 1.0,
        "status": "approved",
    },
    "domicilio": {
        "value": "AV. RIVADAVIA 1234, CIUDAD AUTONOMA DE BUENOS AIRES",
        "confidence": 0.92,
        "status": "approved",
    },
    "dorso_presente": {"value": "SI", "confidence": 0.95, "status": "approved"},
}


class MockExtractor(Extractor):
    """Devuelve una salida fija para probar el pipeline sin invocar al modelo real."""

    def extract(self, file_path: Path, content_type: str) -> DniExtractionResult:
        fields = {
            campo: FieldExtractionSchema.model_validate(payload)
            for campo, payload in _MOCK_PAYLOAD.items()
        }
        return DniExtractionResult(fields=fields, raw_response=_MOCK_PAYLOAD)
