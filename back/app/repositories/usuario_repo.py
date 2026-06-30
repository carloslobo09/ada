from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, usuario_id: str) -> Usuario | None:
        return self._session.get(Usuario, usuario_id)

    def get_by_email(self, email: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.email == email)
        return self._session.scalars(stmt).first()

    def list(self) -> list[Usuario]:
        stmt = select(Usuario).order_by(Usuario.fecha_alta.asc())
        return list(self._session.scalars(stmt))

    def create(
        self,
        *,
        email: str,
        nombre: str,
        rol: str,
        password_hash: str,
    ) -> Usuario:
        usuario = Usuario(
            email=email,
            nombre=nombre,
            rol=rol,
            password_hash=password_hash,
            estado="activo",
        )
        self._session.add(usuario)
        self._session.commit()
        self._session.refresh(usuario)
        return usuario

    def update(
        self,
        usuario: Usuario,
        *,
        nombre: str | None = None,
        rol: str | None = None,
        estado: str | None = None,
        password_hash: str | None = None,
    ) -> Usuario:
        if nombre is not None:
            usuario.nombre = nombre
        if rol is not None:
            usuario.rol = rol
        if estado is not None:
            usuario.estado = estado
        if password_hash is not None:
            usuario.password_hash = password_hash
        self._session.commit()
        self._session.refresh(usuario)
        return usuario
