from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tipo_documento import TipoDocumento


class TipoDocumentoRepository:
    """Acceso a datos para la entidad TipoDocumento."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, tipo_id: str) -> TipoDocumento | None:
        return self._session.get(TipoDocumento, tipo_id)

    def get_by_nombre(self, nombre: str) -> TipoDocumento | None:
        stmt = select(TipoDocumento).where(TipoDocumento.nombre == nombre)
        return self._session.scalars(stmt).first()

    def list(self, *, solo_activos: bool = False) -> list[TipoDocumento]:
        stmt = select(TipoDocumento).order_by(TipoDocumento.nombre.asc())
        if solo_activos:
            stmt = stmt.where(TipoDocumento.estado == "activo")
        return list(self._session.scalars(stmt))

    def create(self, *, nombre: str, descripcion: str | None) -> TipoDocumento:
        tipo = TipoDocumento(nombre=nombre, descripcion=descripcion, estado="activo")
        self._session.add(tipo)
        self._session.commit()
        self._session.refresh(tipo)
        return tipo

    def update(
        self,
        tipo: TipoDocumento,
        *,
        nombre: str | None,
        descripcion: str | None,
        estado: str | None,
    ) -> TipoDocumento:
        if nombre is not None:
            tipo.nombre = nombre
        if descripcion is not None:
            tipo.descripcion = descripcion
        if estado is not None:
            tipo.estado = estado
        self._session.commit()
        self._session.refresh(tipo)
        return tipo

    def delete(self, tipo: TipoDocumento) -> None:
        self._session.delete(tipo)
        self._session.commit()
