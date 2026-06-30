import json
import mimetypes
from pathlib import Path
from typing import Any

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.schemas.extraction import FieldExtractionSchema
from app.services.extraction.errors import (
    ExtractorAuthError,
    ExtractorInvalidResponseError,
    ExtractorRateLimitedError,
    ExtractorUnavailableError,
)
from app.services.extraction.protocol import DniExtractionResult, Extractor


class GeminiExtractor(Extractor):
    """Adaptador del extractor para Google Gemini con salida condicionada por JSON Schema."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        prompt: str,
        response_schema: dict[str, Any],
    ) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name
        self._prompt = prompt
        self._response_schema = response_schema

    def extract(self, file_path: Path, content_type: str) -> DniExtractionResult:
        mime_type = content_type or self._guess_mime(file_path)
        file_bytes = file_path.read_bytes()

        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=[
                    self._prompt,
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=self._response_schema,
                    temperature=0.0,
                ),
            )
        except genai_errors.ServerError as exc:
            raise ExtractorUnavailableError(
                f"El modelo Gemini '{self._model_name}' esta sobrecargado o caido "
                "temporalmente. Reintenta en unos segundos."
            ) from exc
        except genai_errors.ClientError as exc:
            status_code = getattr(exc, "code", None)
            if status_code == 429:
                raise ExtractorRateLimitedError(
                    "Cuota o limite de solicitudes superado en Gemini. "
                    "Reintenta mas tarde o revisa el plan de uso."
                ) from exc
            if status_code in (401, 403):
                raise ExtractorAuthError(
                    "Credenciales invalidas o sin permisos para invocar Gemini. "
                    "Revisa GEMINI_API_KEY en la configuracion del backend."
                ) from exc
            raise ExtractorInvalidResponseError(
                f"Gemini rechazo la solicitud: {exc}"
            ) from exc
        except genai_errors.APIError as exc:
            raise ExtractorUnavailableError(
                f"Error inesperado al invocar Gemini: {exc}"
            ) from exc

        try:
            payload = json.loads(response.text)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ExtractorInvalidResponseError(
                "El modelo devolvio una respuesta que no es JSON valido."
            ) from exc

        try:
            fields = {
                campo: FieldExtractionSchema.model_validate(payload[campo])
                for campo in payload
            }
        except (KeyError, ValueError) as exc:
            raise ExtractorInvalidResponseError(
                f"La respuesta del modelo no respeta el contrato esperado: {exc}"
            ) from exc

        return DniExtractionResult(fields=fields, raw_response=payload)

    @staticmethod
    def _guess_mime(file_path: Path) -> str:
        mime, _ = mimetypes.guess_type(file_path)
        return mime or "application/octet-stream"
