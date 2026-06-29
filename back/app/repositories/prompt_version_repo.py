from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.prompt_version import PromptVersion


class PromptVersionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, version_id: str) -> PromptVersion | None:
        return self._session.get(PromptVersion, version_id)

    def get_active(self, tipo_documento_id: str) -> PromptVersion | None:
        stmt = select(PromptVersion).where(
            PromptVersion.tipo_documento_id == tipo_documento_id,
            PromptVersion.estado == "publicada",
        )
        return self._session.scalars(stmt).first()

    def list(self, tipo_documento_id: str | None = None) -> list[PromptVersion]:
        stmt = select(PromptVersion).order_by(PromptVersion.created_at.desc())
        if tipo_documento_id:
            stmt = stmt.where(PromptVersion.tipo_documento_id == tipo_documento_id)
        return list(self._session.scalars(stmt))

    def create(
        self,
        *,
        tipo_documento_id: str,
        prompt_text: str,
        cross_validation_config: list[dict[str, Any]],
        publish: bool = False,
        ref_usuario_creador: str | None = None,
    ) -> PromptVersion:
        numero = self._next_numero(tipo_documento_id)
        version = PromptVersion(
            numero=numero,
            tipo_documento_id=tipo_documento_id,
            prompt_text=prompt_text,
            cross_validation_config=cross_validation_config,
            estado="borrador",
            ref_usuario_creador=ref_usuario_creador,
        )
        self._session.add(version)
        self._session.flush()
        if publish:
            self._publish(version, ref_usuario_publicador=ref_usuario_creador)
        self._session.commit()
        self._session.refresh(version)
        return version

    def publish(
        self, version: PromptVersion, *, ref_usuario_publicador: str | None = None
    ) -> PromptVersion:
        self._publish(version, ref_usuario_publicador=ref_usuario_publicador)
        self._session.commit()
        self._session.refresh(version)
        return version

    def delete(self, version: PromptVersion) -> None:
        self._session.delete(version)
        self._session.commit()

    def _next_numero(self, tipo_documento_id: str) -> int:
        stmt = select(func.max(PromptVersion.numero)).where(
            PromptVersion.tipo_documento_id == tipo_documento_id
        )
        maximo = self._session.scalar(stmt)
        return (maximo or 0) + 1

    def _publish(
        self, version: PromptVersion, *, ref_usuario_publicador: str | None
    ) -> None:
        current = self.get_active(version.tipo_documento_id)
        if current and current.id != version.id:
            current.estado = "archivada"
        version.estado = "publicada"
        version.activated_at = datetime.now(timezone.utc)
        if ref_usuario_publicador is not None:
            version.ref_usuario_publicador = ref_usuario_publicador
