from __future__ import annotations

from app.models.usuario import Usuario
from app.repositories.usuario_repo import UsuarioRepository
from app.services.auth_service import AuthService


class UsuarioNotFoundError(Exception):
    pass


class DuplicateEmailError(Exception):
    pass


class SelfModificationError(Exception):
    """El admin no puede modificarse a si mismo via este endpoint para evitar lockout."""


class UsuarioService:
    def __init__(self, repository: UsuarioRepository, auth_service: AuthService) -> None:
        self._repository = repository
        self._auth_service = auth_service

    def get(self, usuario_id: str) -> Usuario:
        usuario = self._repository.get(usuario_id)
        if usuario is None:
            raise UsuarioNotFoundError(usuario_id)
        return usuario

    def list(self) -> list[Usuario]:
        return self._repository.list()

    def create(
        self, *, email: str, nombre: str, rol: str, password: str
    ) -> Usuario:
        if self._repository.get_by_email(email) is not None:
            raise DuplicateEmailError(email)
        return self._repository.create(
            email=email,
            nombre=nombre,
            rol=rol,
            password_hash=self._auth_service.hash_password(password),
        )

    def update(
        self,
        usuario_id: str,
        *,
        actor_id: str,
        nombre: str | None,
        rol: str | None,
        estado: str | None,
    ) -> Usuario:
        usuario = self.get(usuario_id)
        if usuario.id == actor_id and (rol is not None or estado is not None):
            raise SelfModificationError(
                "No podes cambiar tu propio rol ni estado por esta via."
            )
        return self._repository.update(
            usuario, nombre=nombre, rol=rol, estado=estado
        )

    def reset_password(
        self, usuario_id: str, *, actor_id: str, new_password: str
    ) -> Usuario:
        usuario = self.get(usuario_id)
        if usuario.id == actor_id:
            raise SelfModificationError(
                "No podes resetear tu propia contrasena por esta via."
            )
        return self._repository.update(
            usuario,
            password_hash=self._auth_service.hash_password(new_password),
        )
