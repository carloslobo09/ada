from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.api.dependencies import (
    CurrentUserDep,
    PromptVersionServiceDep,
    SimulationServiceDep,
    require_roles,
)
from app.api.uploads import parse_expected, read_validated_file
from app.models.usuario import Usuario
from app.schemas.prompt_version import (
    PromptVersionCreate,
    PromptVersionListItem,
    PromptVersionOut,
)
from app.schemas.simulation import SimulationOut
from app.services.extraction.errors import (
    ExtractorAuthError,
    ExtractorInvalidResponseError,
    ExtractorRateLimitedError,
    ExtractorUnavailableError,
)
from app.services.prompt_version_service import (
    CannotDeleteActiveVersionError,
    PromptVersionNotFoundError,
)

router = APIRouter(prefix="/prompt-versions", tags=["prompt-versions"])

EntrenadorOAdmin = Annotated[Usuario, Depends(require_roles("entrenador", "admin"))]


@router.get("", response_model=list[PromptVersionListItem])
def list_versions(
    user: CurrentUserDep,
    service: PromptVersionServiceDep,
    tipo_documento_id: Annotated[
        str | None, Query(description="Filtrar por tipo documental.")
    ] = None,
) -> list[PromptVersionListItem]:
    versions = service.list(tipo_documento_id=tipo_documento_id)
    return [PromptVersionListItem.model_validate(v) for v in versions]


@router.get("/{version_id}", response_model=PromptVersionOut)
def get_version(
    version_id: str,
    user: EntrenadorOAdmin,
    service: PromptVersionServiceDep,
) -> PromptVersionOut:
    try:
        version = service.get(version_id)
    except PromptVersionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version no encontrada: {version_id}",
        ) from exc
    return PromptVersionOut.model_validate(version)


@router.post("", response_model=PromptVersionOut, status_code=status.HTTP_201_CREATED)
def create_version(
    payload: PromptVersionCreate,
    user: EntrenadorOAdmin,
    service: PromptVersionServiceDep,
) -> PromptVersionOut:
    version = service.create(
        tipo_documento_id=payload.tipo_documento_id,
        prompt_text=payload.prompt_text,
        extraction_fields=[ef.model_dump() for ef in payload.extraction_fields],
        cross_validation_config=[cf.model_dump() for cf in payload.cross_validation_config],
        ref_usuario_creador=user.id,
    )
    return PromptVersionOut.model_validate(version)


@router.patch("/{version_id}/publish", response_model=PromptVersionOut)
def publish_version(
    version_id: str,
    user: EntrenadorOAdmin,
    service: PromptVersionServiceDep,
) -> PromptVersionOut:
    try:
        version = service.publish(version_id, ref_usuario_publicador=user.id)
    except PromptVersionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version no encontrada: {version_id}",
        ) from exc
    return PromptVersionOut.model_validate(version)


@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_version(
    version_id: str,
    user: EntrenadorOAdmin,
    service: PromptVersionServiceDep,
) -> None:
    try:
        service.delete(version_id)
    except PromptVersionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version no encontrada: {version_id}",
        ) from exc
    except CannotDeleteActiveVersionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar la version publicada. Publica otra version primero.",
        ) from exc


@router.post("/{version_id}/simulate", response_model=SimulationOut)
async def simulate_version(
    version_id: str,
    user: EntrenadorOAdmin,
    service: SimulationServiceDep,
    file: Annotated[UploadFile, File(description="Imagen o PDF del documento de prueba.")],
    expected: Annotated[
        str | None,
        Form(
            description=(
                "JSON opcional con valores esperados para validacion cruzada. "
                'Ejemplo: {"numero_dni": "40629756"}'
            ),
        ),
    ] = None,
) -> SimulationOut:
    content = await read_validated_file(file)
    parsed_expected = parse_expected(expected)

    try:
        return service.simulate(
            version_id=version_id,
            filename=file.filename or "documento",
            content=content,
            content_type=file.content_type,
            expected=parsed_expected,
        )
    except PromptVersionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version no encontrada: {version_id}",
        ) from exc
    except ExtractorAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
        ) from exc
    except ExtractorRateLimitedError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)
        ) from exc
    except ExtractorUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except ExtractorInvalidResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
        ) from exc
