"""Normalizadores aplicables a un valor antes de la comparacion.

Cada normalizador es una funcion str -> str. La lista de normalizaciones de un
campo se aplica en orden, tanto al valor extraido como al esperado, antes de
delegar la comparacion al motor.
"""

import re
import unicodedata
from collections.abc import Callable

from app.domain.cross_validation import NormalizationType


def _trim(value: str) -> str:
    return value.strip()


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value)


def _uppercase(value: str) -> str:
    return value.upper()


def _lowercase(value: str) -> str:
    return value.lower()


def _remove_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _digits_only(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


_NORMALIZERS: dict[NormalizationType, Callable[[str], str]] = {
    NormalizationType.TRIM: _trim,
    NormalizationType.COLLAPSE_SPACES: _collapse_spaces,
    NormalizationType.UPPERCASE: _uppercase,
    NormalizationType.LOWERCASE: _lowercase,
    NormalizationType.REMOVE_ACCENTS: _remove_accents,
    NormalizationType.DIGITS_ONLY: _digits_only,
}


def apply(normalizations: list[NormalizationType], value: str) -> str:
    result = value
    for norm in normalizations:
        result = _NORMALIZERS[norm](result)
    return result
