from typing import Any

from pydantic import BaseModel


class RuleResultOut(BaseModel):
    name: str
    severity: str
    passed: bool
    reason: str


class CrossValidationResultOut(BaseModel):
    field: str
    expected: str
    extracted: str
    comparison: str
    critical: bool
    passed: bool
    reason: str


class SimulationOut(BaseModel):
    """Resultado de una simulacion: shape plano, no se persiste."""

    prompt_version_id: str

    expected_received: dict[str, str] | None
    raw_extraction: dict[str, Any] | None
    normalized_extraction: dict[str, Any] | None
    rule_results: list[RuleResultOut] | None
    cross_validation_results: list[CrossValidationResultOut] | None

    decision_status: str
    decision_reason: str
