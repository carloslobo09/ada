from dataclasses import dataclass
from enum import Enum


class ComparisonType(str, Enum):
    EQUALS = "equals"
    EQUALS_NORMALIZED = "equals_normalized"
    NUMERIC_EQUALS = "numeric_equals"
    FUZZY_60 = "fuzzy_60"
    FUZZY_70 = "fuzzy_70"
    CONTAINS = "contains"


@dataclass(frozen=True)
class CrossField:
    """Configura como se compara un campo extraido contra su valor esperado.

    Atributos:
        field: nombre del campo (coincide con la representacion canonica del DNI).
        comparison: estrategia de comparacion a aplicar.
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
