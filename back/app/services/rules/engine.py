from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from app.domain.extraction import NormalizedExtraction


class Severity(str, Enum):
    CRITICAL = "critical"
    INFORMATIVE = "informative"


@dataclass(frozen=True)
class RuleResult:
    name: str
    severity: Severity
    passed: bool
    reason: str


class Rule(ABC):
    name: str
    severity: Severity

    @abstractmethod
    def check(self, target: NormalizedExtraction) -> RuleResult: ...


class RuleEngine:
    """Aplica una secuencia de reglas sobre una extraccion normalizada."""

    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules

    def evaluate(self, target: NormalizedExtraction) -> list[RuleResult]:
        return [rule.check(target) for rule in self._rules]
