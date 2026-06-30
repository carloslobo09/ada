from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.documento import Documento


class DocumentoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        tipo_documento_id: str,
        nombre_original: str,
        ubicacion_s3: str,
        hash_integridad: str,
        content_type: str,
        file_size: int,
    ) -> Documento:
        documento = Documento(
            tipo_documento_id=tipo_documento_id,
            nombre_original=nombre_original,
            ubicacion_s3=ubicacion_s3,
            hash_integridad=hash_integridad,
            content_type=content_type,
            file_size=file_size,
        )
        self._session.add(documento)
        self._session.commit()
        self._session.refresh(documento)
        return documento

    def get(self, documento_id: str) -> Documento | None:
        return self._session.get(Documento, documento_id)
