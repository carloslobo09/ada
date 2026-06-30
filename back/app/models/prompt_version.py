import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    numero: Mapped[int] = mapped_column(Integer)

    tipo_documento_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tipos_documento.id"), index=True
    )

    prompt_text: Mapped[str] = mapped_column(String)
    extraction_fields: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    cross_validation_config: Mapped[list[dict[str, Any]]] = mapped_column(JSON)

    estado: Mapped[str] = mapped_column(String(16), default="borrador")

    ref_usuario_creador: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=True
    )
    ref_usuario_publicador: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
