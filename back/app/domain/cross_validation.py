from dataclasses import dataclass, field
from enum import Enum


class NormalizationType(str, Enum):
    TRIM = "trim"
    COLLAPSE_SPACES = "collapse_spaces"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    REMOVE_ACCENTS = "remove_accents"
    DIGITS_ONLY = "digits_only"


class ComparisonType(str, Enum):
    EQUALS = "equals"
    FUZZY_60 = "fuzzy_60"
    FUZZY_70 = "fuzzy_70"
    CONTAINS = "contains"


@dataclass(frozen=True)
class CrossField:
    """Configura como se normaliza y compara un campo extraido contra su valor esperado.

    Atributos:
        field: nombre del campo (coincide con la representacion canonica del DNI).
        normalization: lista de normalizadores que se aplican en orden a ambos
            valores (extraido y esperado) antes de la comparacion. Lista vacia
            implica comparacion sin transformacion previa.
        comparison: estrategia de comparacion a aplicar despues de normalizar.
        critical: si la comparacion falla, baja la decision a REJECTED.
            Si esta en False, la comparacion no afecta la decision: queda como
            observacion en el motivo cuando falla.
        required_expected: el cliente debe enviar este campo en su payload.
            Si no lo envia, el caso se rechaza pre-LLM sin invocar al modelo.
    """

    field: str
    comparison: ComparisonType
    critical: bool
    required_expected: bool = False
    normalization: list[NormalizationType] = field(default_factory=list)


@dataclass(frozen=True)
class CrossValidationResult:
    """Resultado de comparar un campo extraido contra el valor esperado del cliente."""

    field: str
    expected: str
    extracted: str
    comparison: ComparisonType
    critical: bool
    passed: bool
    reason: str
    normalization: list[NormalizationType] = field(default_factory=list)
