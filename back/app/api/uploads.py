"""Validaciones compartidas para endpoints que reciben documentos multipart."""

import json

from fastapi import HTTPException, UploadFile, status

ALLOWED_MIME: frozenset[str] = frozenset(
    {"image/jpeg", "image/png", "image/webp", "application/pdf"}
)
MAX_BYTES = 10 * 1024 * 1024


async def read_validated_file(file: UploadFile) -> bytes:
    """Valida MIME y tamano del archivo subido y devuelve su contenido."""
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
    return content


def parse_expected(raw: str | None) -> dict[str, str] | None:
    """Parsea el campo multipart `expected` (JSON de valores de referencia)."""
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
