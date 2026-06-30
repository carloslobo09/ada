from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class NormalizedExtraction:
    """Representacion canonica de los campos extraidos por el LLM.

    Generica para cualquier tipo de documento: los nombres de campo provienen de
    la configuracion `extraction_fields` de la version de prompt usada.
    """

    values: dict[str, str]
    confidences: dict[str, float] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
