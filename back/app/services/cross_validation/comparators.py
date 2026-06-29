import unicodedata
from collections.abc import Callable
from difflib import SequenceMatcher

from app.domain.cross_validation import ComparisonType


def _strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _normalize(value: str) -> str:
    return _strip_accents(value).strip().casefold()


def _digits_only(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def equals(extracted: str, expected: str) -> tuple[bool, str]:
    if extracted == expected:
        return True, "Coincidencia exacta."
    return False, f"Esperado '{expected}', obtenido '{extracted}'."


def equals_normalized(extracted: str, expected: str) -> tuple[bool, str]:
    if _normalize(extracted) == _normalize(expected):
        return True, "Coincidencia normalizada (sin acentos, sin mayusculas)."
    return False, f"Esperado '{expected}', obtenido '{extracted}'."


def numeric_equals(extracted: str, expected: str) -> tuple[bool, str]:
    if _digits_only(extracted) == _digits_only(expected):
        return True, "Coincidencia numerica."
    return False, f"Esperado '{expected}', obtenido '{extracted}'."


def fuzzy(threshold: float) -> Callable[[str, str], tuple[bool, str]]:
    """Devuelve un comparador que requiere ratio de similitud >= threshold (0..1)."""

    def _compare(extracted: str, expected: str) -> tuple[bool, str]:
        ratio = SequenceMatcher(None, _normalize(extracted), _normalize(expected)).ratio()
        if ratio >= threshold:
            return True, f"Similitud {ratio:.2f} >= {threshold:.2f}."
        return False, (
            f"Similitud {ratio:.2f} < {threshold:.2f}. "
            f"Esperado '{expected}', obtenido '{extracted}'."
        )

    return _compare


def contains(extracted: str, expected: str) -> tuple[bool, str]:
    if _normalize(expected) in _normalize(extracted):
        return True, "El valor esperado esta contenido en el extraido."
    return False, f"'{expected}' no se encuentra dentro de '{extracted}'."


_COMPARATORS: dict[ComparisonType, Callable[[str, str], tuple[bool, str]]] = {
    ComparisonType.EQUALS: equals,
    ComparisonType.EQUALS_NORMALIZED: equals_normalized,
    ComparisonType.NUMERIC_EQUALS: numeric_equals,
    ComparisonType.FUZZY_60: fuzzy(0.60),
    ComparisonType.FUZZY_70: fuzzy(0.70),
    ComparisonType.CONTAINS: contains,
}


def compare(comparison: ComparisonType, extracted: str, expected: str) -> tuple[bool, str]:
    return _COMPARATORS[comparison](extracted, expected)
