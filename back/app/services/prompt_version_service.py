from __future__ import annotations

from typing import Any

from app.models.prompt_version import PromptVersion
from app.repositories.prompt_version_repo import PromptVersionRepository


class PromptVersionNotFoundError(Exception):
    pass


class CannotDeleteActiveVersionError(Exception):
    pass


class PromptVersionService:
    def __init__(self, repository: PromptVersionRepository) -> None:
        self._repository = repository

    def get(self, version_id: str) -> PromptVersion:
        version = self._repository.get(version_id)
        if version is None:
            raise PromptVersionNotFoundError(version_id)
        return version

    def get_active_or_raise(self, tipo_documento_id: str) -> PromptVersion:
        version = self._repository.get_active(tipo_documento_id)
        if version is None:
            raise PromptVersionNotFoundError(tipo_documento_id)
        return version

    def list(self, tipo_documento_id: str | None = None) -> list[PromptVersion]:
        return self._repository.list(tipo_documento_id=tipo_documento_id)

    def create(
        self,
        *,
        tipo_documento_id: str,
        prompt_text: str,
        cross_validation_config: list[dict[str, Any]],
        ref_usuario_creador: str | None = None,
    ) -> PromptVersion:
        return self._repository.create(
            tipo_documento_id=tipo_documento_id,
            prompt_text=prompt_text,
            cross_validation_config=cross_validation_config,
            publish=False,
            ref_usuario_creador=ref_usuario_creador,
        )

    def publish(
        self, version_id: str, *, ref_usuario_publicador: str | None = None
    ) -> PromptVersion:
        version = self.get(version_id)
        return self._repository.publish(
            version, ref_usuario_publicador=ref_usuario_publicador
        )

    def delete(self, version_id: str) -> None:
        version = self.get(version_id)
        if version.estado == "publicada":
            raise CannotDeleteActiveVersionError(version_id)
        self._repository.delete(version)


def seed_default_prompt_version_if_missing(
    repository: PromptVersionRepository,
    *,
    tipo_documento_id: str,
    prompt_text: str,
    cross_validation_config: list[dict[str, Any]],
) -> None:
    if repository.get_active(tipo_documento_id) is not None:
        return
    repository.create(
        tipo_documento_id=tipo_documento_id,
        prompt_text=prompt_text,
        cross_validation_config=cross_validation_config,
        publish=True,
    )
