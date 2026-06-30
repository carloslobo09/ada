import json
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.api.dependencies import (
    CasoRepositoryDep,
    CurrentUserDep,
    PromptVersionServiceDep,
    SessionDep,
    SettingsDep,
    build_caso_service_for_tipo,
    get_storage,
    require_roles,
)
from app.models.usuario import Usuario
from app.schemas.caso import (
    CasoClienteListItem,
    CasoClienteListOut,
    CasoClienteOut,
    CasoListItem,
    CasoListOut,
    CasoOut,
    ReviewRequest,
    to_cliente_list_item,
    to_cliente_out,
)
from app.services.extraction.errors import (
    ExtractorAuthError,
    ExtractorInvalidResponseError,
    ExtractorRateLimitedError,
    ExtractorUnavailableError,
)
from app.storage.filesystem import FilesystemStorage

router = APIRouter(prefix="/cases", tags=["cases"])

ALLOWED_MIME: frozenset[str] = frozenset(
    {"image/jpeg", "image/png", "image/webp", "application/pdf"}
)
MAX_BYTES = 10 * 1024 * 1024


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_case(
    user: CurrentUserDep,
    session: SessionDep,
    settings: SettingsDep,
    storage: Annotated[FilesystemStorage, Depends(get_storage)],
    prompt_version_service: PromptVersionServiceDep,
    file: Annotated[UploadFile, File(description="Imagen o PDF del documento a auditar.")],
    tipo_documento_id: Annotated[
        str, Form(description="Identificador del tipo de documento a procesar.")
    ],
    expected: Annotated[
        str | None,
        Form(
            description=(
                "JSON con valores esperados para validacion cruzada. "
                'Ejemplo: {"numero_dni": "40629756"}'
            ),
        ),
    ] = None,
) -> CasoOut | CasoClienteOut:
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

    service = build_caso_service_for_tipo(
        session=session,
        settings=settings,
        storage=storage,
        prompt_version_service=prompt_version_service,
        tipo_documento_id=tipo_documento_id,
    )

    try:
        caso = service.process(
            filename=file.filename or "documento",
            content=content,
            content_type=file.content_type,
            expected=parsed_expected,
            ref_usuario_cliente=user.id,
        )
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

    if user.rol == "cliente":
        return to_cliente_out(caso)
    return CasoOut.model_validate(caso)


@router.get("/{case_id}")
def get_case(
    case_id: str,
    user: CurrentUserDep,
    repository: CasoRepositoryDep,
) -> CasoOut | CasoClienteOut:
    caso = repository.get(case_id)
    if caso is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado.")
    _ensure_visible_to_user(caso, user)
    if user.rol == "cliente":
        return to_cliente_out(caso)
    return CasoOut.model_validate(caso)


@router.get("")
def list_cases(
    user: CurrentUserDep,
    repository: CasoRepositoryDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    recontrol: Literal["pendiente", "correcto", "incorrecto"] | None = Query(
        default=None, description="Filtra la bandeja por estado de Re Control."
    ),
) -> CasoListOut | CasoClienteListOut:
    ref = user.id if user.rol == "cliente" else None
    casos = repository.list(
        limit=limit,
        offset=offset,
        estado_recontrol=recontrol,
        ref_usuario_cliente=ref,
    )
    if user.rol == "cliente":
        return CasoClienteListOut(
            items=[to_cliente_list_item(c) for c in casos],
            limit=limit,
            offset=offset,
        )
    return CasoListOut(
        items=[CasoListItem.model_validate(c) for c in casos],
        limit=limit,
        offset=offset,
    )


@router.patch("/{case_id}/review", response_model=CasoOut)
def review_case(
    case_id: str,
    payload: ReviewRequest,
    user: Annotated[Usuario, Depends(require_roles("entrenador", "admin"))],
    repository: CasoRepositoryDep,
) -> CasoOut:
    caso = repository.get(case_id)
    if caso is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado.")
    updated = repository.mark_review(
        caso,
        estado_recontrol=payload.estado_recontrol,
        observacion_recontrol=payload.observacion_recontrol,
        ref_usuario_recontrol=user.id,
    )
    return CasoOut.model_validate(updated)


def _ensure_visible_to_user(caso, user: Usuario) -> None:
    if user.rol == "cliente" and caso.ref_usuario_cliente != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado."
        )


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
