from typing import Any

from app.config import Settings
from app.schemas.extraction import build_response_schema
from app.services.extraction.gemini import GeminiExtractor
from app.services.extraction.mock import MockExtractor
from app.services.extraction.protocol import Extractor


def build_extractor(
    settings: Settings,
    prompt_text: str,
    extraction_fields: list[dict[str, Any]],
) -> Extractor:
    """Construye el extractor segun el modo configurado.

    El response_schema se arma dinamicamente desde `extraction_fields` (definidos
    en la version de prompt vigente), lo que permite al sistema operar sobre
    cualquier tipo documental sin hardcodear campos.

    Lanza RuntimeError si se solicita modo gemini sin API key.
    """
    if settings.extractor_mode == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError(
                "EXTRACTOR_MODE=gemini requiere la variable GEMINI_API_KEY definida."
            )
        return GeminiExtractor(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model,
            prompt=prompt_text,
            response_schema=build_response_schema(extraction_fields),
        )
    return MockExtractor(extraction_fields=extraction_fields)
