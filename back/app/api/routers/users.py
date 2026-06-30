from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import AuthServiceDep, CurrentUserDep, require_roles
from app.db import get_session
from app.models.usuario import Usuario
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import (
    PasswordResetRequest,
    UsuarioCreate,
    UsuarioOut,
    UsuarioUpdate,
)
from app.services.auth_service import AuthService
from app.services.usuario_service import (
    DuplicateEmailError,
    SelfModificationError,
    UsuarioNotFoundError,
    UsuarioService,
)

router = APIRouter(prefix="/users", tags=["users"])


def get_usuario_service(
    session: Annotated[Session, Depends(get_session)],
    auth_service: AuthServiceDep,
) -> UsuarioService:
    return UsuarioService(UsuarioRepository(session), auth_service)


ServiceDep = Annotated[UsuarioService, Depends(get_usuario_service)]
AdminDep = Annotated[Usuario, Depends(require_roles("admin"))]


@router.get("", response_model=list[UsuarioOut])
def list_users(actor: AdminDep, service: ServiceDep) -> list[UsuarioOut]:
    return [UsuarioOut.model_validate(u) for u in service.list()]


@router.get("/{usuario_id}", response_model=UsuarioOut)
def get_user(usuario_id: str, actor: AdminDep, service: ServiceDep) -> UsuarioOut:
    try:
        usuario = service.get(usuario_id)
    except UsuarioNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado."
        ) from exc
    return UsuarioOut.model_validate(usuario)


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UsuarioCreate, actor: AdminDep, service: ServiceDep
) -> UsuarioOut:
    try:
        usuario = service.create(
            email=payload.email,
            nombre=payload.nombre,
            rol=payload.rol,
            password=payload.password,
        )
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un usuario con el email '{payload.email}'.",
        ) from exc
    return UsuarioOut.model_validate(usuario)


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def update_user(
    usuario_id: str,
    payload: UsuarioUpdate,
    actor: AdminDep,
    service: ServiceDep,
) -> UsuarioOut:
    try:
        usuario = service.update(
            usuario_id,
            actor_id=actor.id,
            nombre=payload.nombre,
            rol=payload.rol,
            estado=payload.estado,
        )
    except UsuarioNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado."
        ) from exc
    except SelfModificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    return UsuarioOut.model_validate(usuario)


@router.post("/{usuario_id}/reset-password", response_model=UsuarioOut)
def reset_password(
    usuario_id: str,
    payload: PasswordResetRequest,
    actor: AdminDep,
    service: ServiceDep,
) -> UsuarioOut:
    try:
        usuario = service.reset_password(
            usuario_id, actor_id=actor.id, new_password=payload.new_password
        )
    except UsuarioNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado."
        ) from exc
    except SelfModificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    return UsuarioOut.model_validate(usuario)
