import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Decision(Base):
    """Resultado final del proceso de validacion.

    El campo `refs_evidencias` agrupa, como JSON estructurado, el linaje tecnico
    interno: SalidaModelo, ResultadoExtraccion y EvaluacionReglas. La separacion en
    tablas dedicadas se difiere a la version productiva; aqui se preserva la
    trazabilidad integral por caso conservando el contenido literal de cada paso.
    """

    __tablename__ = "decisiones"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    veredicto: Mapped[str] = mapped_column(String(32))
    motivos: Mapped[str] = mapped_column(String(2048))
    confianza_global: Mapped[float | None] = mapped_column(Float, nullable=True)

    refs_evidencias: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    expected_received: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    cross_validation_results: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON, nullable=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
