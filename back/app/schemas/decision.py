from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DecisionOut(BaseModel):
    id: str
    veredicto: str
    motivos: str
    confianza_global: float | None
    refs_evidencias: dict[str, Any] | None
    expected_received: dict[str, str] | None
    cross_validation_results: list[dict[str, Any]] | None
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
