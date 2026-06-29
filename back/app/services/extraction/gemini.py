import json
import mimetypes
from pathlib import Path

from google import genai
from google.genai import types

from app.schemas.extraction import DNI_RESPONSE_SCHEMA, FieldExtractionSchema
from app.services.extraction.protocol import DniExtractionResult, Extractor


class GeminiExtractor(Extractor):
    """Adaptador del extractor para Google Gemini con salida condicionada por JSON Schema."""

    def __init__(self, api_key: str, model_name: str, prompt: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name
        self._prompt = prompt

    def extract(self, file_path: Path, content_type: str) -> DniExtractionResult:
        mime_type = content_type or self._guess_mime(file_path)
        file_bytes = file_path.read_bytes()

        response = self._client.models.generate_content(
            model=self._model_name,
            contents=[
                self._prompt,
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DNI_RESPONSE_SCHEMA,
                temperature=0.0,
            ),
        )

        payload = json.loads(response.text)
        fields = {
            campo: FieldExtractionSchema.model_validate(payload[campo]) for campo in payload
        }
        return DniExtractionResult(fields=fields, raw_response=payload)

    @staticmethod
    def _guess_mime(file_path: Path) -> str:
        mime, _ = mimetypes.guess_type(file_path)
        return mime or "application/octet-stream"
