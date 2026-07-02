from __future__ import annotations

import re
import unicodedata

from app.models.tipo_documento import TipoDocumento
from app.repositories.prompt_version_repo import PromptVersionRepository
from app.repositories.tipo_documento_repo import TipoDocumentoRepository


class TipoDocumentoNotFoundError(Exception):
    pass


class DuplicateTipoDocumentoError(Exception):
    pass


class TipoDocumentoEnUsoError(Exception):
    """El tipo tiene versiones de prompt asociadas y no puede eliminarse."""


def slugify(nombre: str) -> str:
    decomposed = unicodedata.normalize("NFKD", nombre)
    ascii_only = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    lowered = ascii_only.lower()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")


class TipoDocumentoService:
    """Casos de uso para gestion de tipos documentales.

    `prompt_versions` es opcional: solo hace falta para la operacion delete,
    que rechaza la baja si el tipo tiene versiones asociadas.
    """

    def __init__(
        self,
        repository: TipoDocumentoRepository,
        prompt_versions: PromptVersionRepository | None = None,
    ) -> None:
        self._repository = repository
        self._prompt_versions = prompt_versions

    def get(self, tipo_id: str) -> TipoDocumento:
        tipo = self._repository.get(tipo_id)
        if tipo is None:
            raise TipoDocumentoNotFoundError(tipo_id)
        return tipo

    def list(self, *, solo_activos: bool = False) -> list[TipoDocumento]:
        return self._repository.list(solo_activos=solo_activos)

    def create(self, *, nombre: str, descripcion: str | None) -> TipoDocumento:
        slug = slugify(nombre)
        if (
            self._repository.get_by_nombre(nombre) is not None
            or self._repository.get_by_slug(slug) is not None
        ):
            raise DuplicateTipoDocumentoError(nombre)
        return self._repository.create(
            nombre=nombre, slug=slug, descripcion=descripcion
        )

    def update(
        self,
        tipo_id: str,
        *,
        nombre: str | None,
        descripcion: str | None,
        estado: str | None,
    ) -> TipoDocumento:
        tipo = self.get(tipo_id)
        if nombre is not None and nombre != tipo.nombre:
            existente = self._repository.get_by_nombre(nombre)
            if existente is not None and existente.id != tipo.id:
                raise DuplicateTipoDocumentoError(nombre)
        return self._repository.update(
            tipo, nombre=nombre, descripcion=descripcion, estado=estado
        )

    def delete(self, tipo_id: str) -> None:
        tipo = self.get(tipo_id)
        if self._prompt_versions is not None and self._prompt_versions.list(tipo.id):
            raise TipoDocumentoEnUsoError(tipo_id)
        self._repository.delete(tipo)


def seed_default_tipo_documento_if_missing(
    repository: TipoDocumentoRepository,
    *,
    nombre: str,
    descripcion: str,
) -> TipoDocumento:
    """Inserta el tipo documental seed si no existe. Devuelve el tipo (creado o existente)."""
    existing = repository.get_by_nombre(nombre)
    if existing is not None:
        return existing
    return repository.create(
        nombre=nombre, slug=slugify(nombre), descripcion=descripcion
    )
