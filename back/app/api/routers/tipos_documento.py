from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUserDep, require_roles
from app.db import get_session
from app.models.usuario import Usuario
from app.repositories.tipo_documento_repo import TipoDocumentoRepository
from app.schemas.tipo_documento import (
    TipoDocumentoCreate,
    TipoDocumentoOut,
    TipoDocumentoUpdate,
)
from app.services.tipo_documento_service import (
    DuplicateTipoDocumentoError,
    TipoDocumentoNotFoundError,
    TipoDocumentoService,
)

router = APIRouter(prefix="/document-types", tags=["document-types"])


def get_tipo_documento_service(
    session: Annotated[Session, Depends(get_session)],
) -> TipoDocumentoService:
    return TipoDocumentoService(TipoDocumentoRepository(session))


ServiceDep = Annotated[TipoDocumentoService, Depends(get_tipo_documento_service)]
AdminDep = Annotated[Usuario, Depends(require_roles("admin"))]


@router.get("", response_model=list[TipoDocumentoOut])
def list_tipos(
    user: CurrentUserDep,
    service: ServiceDep,
    solo_activos: bool = Query(default=False, description="Filtrar solo los activos."),
) -> list[TipoDocumentoOut]:
    tipos = service.list(solo_activos=solo_activos)
    return [TipoDocumentoOut.model_validate(t) for t in tipos]


@router.get("/{tipo_id}", response_model=TipoDocumentoOut)
def get_tipo(
    tipo_id: str,
    user: CurrentUserDep,
    service: ServiceDep,
) -> TipoDocumentoOut:
    try:
        tipo = service.get(tipo_id)
    except TipoDocumentoNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de documento no encontrado: {tipo_id}",
        ) from exc
    return TipoDocumentoOut.model_validate(tipo)


@router.post("", response_model=TipoDocumentoOut, status_code=status.HTTP_201_CREATED)
def create_tipo(
    payload: TipoDocumentoCreate,
    user: AdminDep,
    service: ServiceDep,
) -> TipoDocumentoOut:
    try:
        tipo = service.create(nombre=payload.nombre, descripcion=payload.descripcion)
    except DuplicateTipoDocumentoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un tipo de documento con el nombre '{payload.nombre}'.",
        ) from exc
    return TipoDocumentoOut.model_validate(tipo)


@router.patch("/{tipo_id}", response_model=TipoDocumentoOut)
def update_tipo(
    tipo_id: str,
    payload: TipoDocumentoUpdate,
    user: AdminDep,
    service: ServiceDep,
) -> TipoDocumentoOut:
    try:
        tipo = service.update(
            tipo_id,
            nombre=payload.nombre,
            descripcion=payload.descripcion,
            estado=payload.estado,
        )
    except TipoDocumentoNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de documento no encontrado: {tipo_id}",
        ) from exc
    except DuplicateTipoDocumentoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un tipo de documento con ese nombre.",
        ) from exc
    return TipoDocumentoOut.model_validate(tipo)


@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo(tipo_id: str, user: AdminDep, service: ServiceDep) -> None:
    try:
        service.delete(tipo_id)
    except TipoDocumentoNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de documento no encontrado: {tipo_id}",
        ) from exc
