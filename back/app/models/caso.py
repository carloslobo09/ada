import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.decision import Decision
from app.models.documento import Documento


class Caso(Base):
    """Solicitud de validacion recibida por la API."""

    __tablename__ = "casos"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    estado: Mapped[str] = mapped_column(String(32), default="recibido")

    ref_documento: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("documentos.id"), nullable=True
    )
    ref_decision: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("decisiones.id"), nullable=True
    )
    ref_usuario_cliente: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=True
    )

    estado_recontrol: Mapped[str] = mapped_column(String(16), default="pendiente")
    observacion_recontrol: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    ref_usuario_recontrol: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=True
    )
    fecha_recontrol: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    documento: Mapped[Documento | None] = relationship("Documento", lazy="joined")
    decision: Mapped[Decision | None] = relationship("Decision", lazy="joined")
