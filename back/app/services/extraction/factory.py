from app.config import Settings
from app.services.extraction.gemini import GeminiExtractor
from app.services.extraction.mock import MockExtractor
from app.services.extraction.protocol import Extractor


def build_extractor(settings: Settings, prompt_text: str) -> Extractor:
    """Construye el extractor segun el modo configurado en la aplicacion.

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
        )
    return MockExtractor()
