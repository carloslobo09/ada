from app.domain.extraction import NormalizedExtraction
from app.services.extraction.protocol import DniExtractionResult


def normalize_extraction(extraction: DniExtractionResult) -> NormalizedExtraction:
    """Convierte la salida cruda del extractor en la representacion canonica.

    Aplica un strip basico al value de cada campo. Las normalizaciones
    especificas (uppercase, digits_only, etc.) son responsabilidad del motor de
    validacion cruzada por campo.
    """
    values = {name: f.value.strip() for name, f in extraction.fields.items()}
    confidences = {name: f.confidence for name, f in extraction.fields.items()}
    return NormalizedExtraction(
        values=values, confidences=confidences, raw=extraction.raw_response
    )
