from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.config import Settings
from app.models.usuario import Usuario
from app.repositories.usuario_repo import UsuarioRepository

_BCRYPT_MAX_BYTES = 72


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class AuthService:
    def __init__(self, repository: UsuarioRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    def hash_password(self, password: str) -> str:
        secret = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
        return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        secret = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
        try:
            return bcrypt.checkpw(secret, hashed.encode("utf-8"))
        except ValueError:
            return False

    def authenticate(self, email: str, password: str) -> Usuario:
        user = self._repository.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError()
        if not self.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        if user.estado != "activo":
            raise InactiveUserError()
        return user

    def create_access_token(self, user: Usuario) -> str:
        now = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "sub": user.id,
            "email": user.email,
            "rol": user.rol,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._settings.jwt_expire_minutes)).timestamp()),
        }
        return jwt.encode(
            payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm]
            )
        except jwt.PyJWTError as exc:
            raise InvalidTokenError(str(exc)) from exc

    def get_user_from_token(self, token: str) -> Usuario:
        payload = self.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("missing sub")
        user = self._repository.get(user_id)
        if user is None:
            raise InvalidTokenError("user not found")
        if user.estado != "activo":
            raise InactiveUserError()
        return user


def seed_default_users_if_missing(
    repository: UsuarioRepository,
    *,
    auth_service: AuthService,
    password: str,
) -> None:
    """Inserta 3 usuarios seed (admin, entrenador, cliente) si no existen."""
    seeds = [
        ("admin@ada.local", "Administrador ADA", "admin"),
        ("entrenador@ada.local", "Entrenador ADA", "entrenador"),
        ("cliente@ada.local", "Cliente ADA", "cliente"),
    ]
    for email, nombre, rol in seeds:
        if repository.get_by_email(email) is None:
            repository.create(
                email=email,
                nombre=nombre,
                rol=rol,
                password_hash=auth_service.hash_password(password),
            )
