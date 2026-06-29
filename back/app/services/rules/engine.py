from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class Severity(str, Enum):
    CRITICAL = "critical"
    INFORMATIVE = "informative"


@dataclass(frozen=True)
class RuleResult:
    name: str
    severity: Severity
    passed: bool
    reason: str


class Rule(ABC, Generic[T]):
    name: str
    severity: Severity

    @abstractmethod
    def check(self, target: T) -> RuleResult: ...


class RuleEngine(Generic[T]):
    """Aplica una secuencia de reglas sobre un input normalizado."""

    def __init__(self, rules: list[Rule[T]]) -> None:
        self._rules = rules

    def evaluate(self, target: T) -> list[RuleResult]:
        return [rule.check(target) for rule in self._rules]
