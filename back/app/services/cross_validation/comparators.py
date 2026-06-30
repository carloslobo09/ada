from collections.abc import Callable
from difflib import SequenceMatcher

from app.domain.cross_validation import ComparisonType


def equals(extracted: str, expected: str) -> tuple[bool, str]:
    if extracted == expected:
        return True, "Coincidencia exacta."
    return False, f"Esperado '{expected}', obtenido '{extracted}'."


def fuzzy(threshold: float) -> Callable[[str, str], tuple[bool, str]]:
    """Devuelve un comparador que requiere ratio de similitud >= threshold (0..1)."""

    def _compare(extracted: str, expected: str) -> tuple[bool, str]:
        ratio = SequenceMatcher(None, extracted, expected).ratio()
        if ratio >= threshold:
            return True, f"Similitud {ratio:.2f} >= {threshold:.2f}."
        return False, (
            f"Similitud {ratio:.2f} < {threshold:.2f}. "
            f"Esperado '{expected}', obtenido '{extracted}'."
        )

    return _compare


def contains(extracted: str, expected: str) -> tuple[bool, str]:
    if expected in extracted:
        return True, "El valor esperado esta contenido en el extraido."
    return False, f"'{expected}' no se encuentra dentro de '{extracted}'."


_COMPARATORS: dict[ComparisonType, Callable[[str, str], tuple[bool, str]]] = {
    ComparisonType.EQUALS: equals,
    ComparisonType.FUZZY_60: fuzzy(0.60),
    ComparisonType.FUZZY_70: fuzzy(0.70),
    ComparisonType.CONTAINS: contains,
}


def compare(comparison: ComparisonType, extracted: str, expected: str) -> tuple[bool, str]:
    return _COMPARATORS[comparison](extracted, expected)
