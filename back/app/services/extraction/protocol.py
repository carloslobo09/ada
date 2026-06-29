from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.schemas.extraction import FieldExtractionSchema


@dataclass(frozen=True)
class DniExtractionResult:
    """Salida del extractor: campos parseados y respuesta cruda del modelo."""

    fields: dict[str, FieldExtractionSchema]
    raw_response: dict[str, Any]


class Extractor(ABC):
    """Puerto del extractor LLM. Cada adaptador implementa una estrategia concreta."""

    @abstractmethod
    def extract(self, file_path: Path, content_type: str) -> DniExtractionResult: ...
