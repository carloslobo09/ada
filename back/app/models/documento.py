import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Documento(Base):
    """Archivo recibido y su ubicacion en el almacenamiento de evidencias.

    En la version productiva la `ubicacion_s3` apunta a un bucket S3 con versionado.
    En el MVP local apunta a la ruta del filesystem montado como volumen Docker.
    """

    __tablename__ = "documentos"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tipo_documento_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tipos_documento.id"), index=True
    )

    ubicacion_s3: Mapped[str] = mapped_column(String(512))
    hash_integridad: Mapped[str] = mapped_column(String(64), index=True)
    fecha_recepcion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    content_type: Mapped[str] = mapped_column(String(128))
    file_size: Mapped[int] = mapped_column(Integer)
