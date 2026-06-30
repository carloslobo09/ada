from app.domain.cross_validation import NormalizationType
from app.services.cross_validation.normalizers import apply


def test_trim() -> None:
    assert apply([NormalizationType.TRIM], "  hola  ") == "hola"


def test_collapse_spaces() -> None:
    assert apply([NormalizationType.COLLAPSE_SPACES], "hola   mundo") == "hola mundo"


def test_uppercase() -> None:
    assert apply([NormalizationType.UPPERCASE], "Hola") == "HOLA"


def test_lowercase() -> None:
    assert apply([NormalizationType.LOWERCASE], "HOLA") == "hola"


def test_remove_accents() -> None:
    assert apply([NormalizationType.REMOVE_ACCENTS], "Núñez Córdoba") == "Nunez Cordoba"


def test_digits_only() -> None:
    assert apply([NormalizationType.DIGITS_ONLY], "40.123.456") == "40123456"


def test_pipeline_combina_en_orden() -> None:
    result = apply(
        [
            NormalizationType.TRIM,
            NormalizationType.UPPERCASE,
            NormalizationType.REMOVE_ACCENTS,
            NormalizationType.COLLAPSE_SPACES,
        ],
        "  josé   pérez  ",
    )
    assert result == "JOSE PEREZ"


def test_lista_vacia_devuelve_el_valor_original() -> None:
    assert apply([], "  hola  ") == "  hola  "
