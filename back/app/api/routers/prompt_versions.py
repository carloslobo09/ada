import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.api.dependencies import (
    CurrentUserDep,
    PromptVersionServiceDep,
    SimulationServiceDep,
    require_roles,
)
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

ALLOWED_MIME: frozenset[str] = frozenset(
    {"image/jpeg", "image/png", "image/webp", "application/pdf"}
)
MAX_BYTES = 10 * 1024 * 1024

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
    user: CurrentUserDep,
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
            detail="No se puede eliminar la version activa. Activa otra version primero.",
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
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no soportado: {file.content_type}",
        )

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el limite de {MAX_BYTES // (1024 * 1024)} MB.",
        )

    parsed_expected = _parse_expected(expected)

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


def _parse_expected(raw: str | None) -> dict[str, str] | None:
    if raw is None or raw.strip() == "":
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo 'expected' no es un JSON valido: {exc.msg}.",
        ) from exc
    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'expected' debe ser un objeto JSON con pares campo: valor.",
        )
    invalid_values = [k for k, v in parsed.items() if not isinstance(v, str)]
    if invalid_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Todos los valores en 'expected' deben ser strings. "
                f"Campos invalidos: {', '.join(invalid_values)}."
            ),
        )
    return parsed
