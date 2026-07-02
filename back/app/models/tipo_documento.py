import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TipoDocumento(Base):
    """Tipo documental que el sistema puede procesar.

    El `slug` se genera al crear el tipo y no cambia aunque se renombre: es la
    clave estable con la que el registry de reglas internas asocia sus reglas.
    """

    __tablename__ = "tipos_documento"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    nombre: Mapped[str] = mapped_column(String(120), unique=True)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    estado: Mapped[str] = mapped_column(String(16), default="activo")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
