from datetime import date

from app.domain.dni import NormalizedDni
from app.services.extraction.protocol import DniExtractionResult


def normalize_dni(extraction: DniExtractionResult) -> NormalizedDni:
    """Convierte la salida cruda del extractor en la representacion canonica del DNI."""
    fields = extraction.fields

    def value_of(key: str) -> str:
        field = fields.get(key)
        return field.value if field else ""

    def confidence_of(key: str) -> float:
        field = fields.get(key)
        return field.confidence if field else 0.0

    numero = value_of("numero_dni")
    for separador in (".", "-", " "):
        numero = numero.replace(separador, "")

    return NormalizedDni(
        numero_dni=numero,
        nombre_completo=value_of("nombre_completo").strip().upper(),
        fecha_nacimiento=_parse_iso_date(value_of("fecha_nacimiento")),
        fecha_emision=_parse_iso_date(value_of("fecha_emision")),
        fecha_vencimiento=_parse_iso_date(value_of("fecha_vencimiento")),
        sexo=value_of("sexo").strip().upper(),
        nacionalidad=value_of("nacionalidad").strip(),
        lugar_nacimiento=value_of("lugar_nacimiento").strip().upper(),
        numero_tramite=value_of("numero_tramite").strip(),
        tipo_documento=value_of("tipo_documento").strip(),
        domicilio=value_of("domicilio").strip().upper(),
        dorso_presente=value_of("dorso_presente").strip().upper() == "SI",
        confianzas={key: confidence_of(key) for key in fields},
    )


def _parse_iso_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
