from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class NormalizedDni:
    """Representacion canonica de los campos extraidos de un DNI argentino."""

    numero_dni: str
    nombre_completo: str
    fecha_nacimiento: date | None
    fecha_emision: date | None
    fecha_vencimiento: date | None
    sexo: str
    nacionalidad: str
    lugar_nacimiento: str
    numero_tramite: str
    tipo_documento: str
    domicilio: str
    dorso_presente: bool
    confianzas: dict[str, float] = field(default_factory=dict)
