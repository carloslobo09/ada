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
