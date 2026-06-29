from dataclasses import dataclass
from typing import Any

from app.domain.cross_validation import ComparisonType, CrossField, CrossValidationResult
from app.services.cross_validation.comparators import compare


@dataclass(frozen=True)
class PreflightOutcome:
    """Resultado de la pre-validacion del payload del cliente antes de invocar al LLM."""

    rejected: bool
    missing_required: list[str]
    unknown_fields: list[str]

    def reason(self) -> str:
        parts: list[str] = []
        if self.missing_required:
            parts.append(
                "Faltan parametros requeridos para la validacion cruzada: "
                + ", ".join(self.missing_required)
            )
        if self.unknown_fields:
            parts.append(
                "Parametros no configurados para el tipo de documento: "
                + ", ".join(self.unknown_fields)
            )
        return ". ".join(parts) + "." if parts else ""


class CrossValidationEngine:
    """Pre-valida el payload del cliente y evalua las comparaciones por campo."""

    def __init__(self, config: list[CrossField]) -> None:
        self._config = config
        self._by_field = {cf.field: cf for cf in config}

    @classmethod
    def from_config_dicts(cls, raw: list[dict[str, Any]]) -> "CrossValidationEngine":
        """Construye el motor desde la representacion serializada del config."""
        fields = [
            CrossField(
                field=item["field"],
                comparison=ComparisonType(item["comparison"]),
                critical=bool(item["critical"]),
                required_expected=bool(item.get("required_expected", False)),
            )
            for item in raw
        ]
        return cls(fields)

    def preflight(self, expected: dict[str, str]) -> PreflightOutcome:
        required = {cf.field for cf in self._config if cf.required_expected}
        sent = set(expected.keys())
        missing = sorted(required - sent)
        unknown = sorted(sent - {cf.field for cf in self._config})
        return PreflightOutcome(
            rejected=bool(missing or unknown),
            missing_required=missing,
            unknown_fields=unknown,
        )

    def evaluate(
        self,
        extracted_values: dict[str, str],
        expected: dict[str, str],
    ) -> list[CrossValidationResult]:
        results: list[CrossValidationResult] = []
        for field_name, expected_value in expected.items():
            config = self._by_field.get(field_name)
            if config is None:
                continue
            extracted_value = extracted_values.get(field_name, "")
            passed, reason = compare(config.comparison, extracted_value, expected_value)
            results.append(
                CrossValidationResult(
                    field=field_name,
                    expected=expected_value,
                    extracted=extracted_value,
                    comparison=config.comparison,
                    critical=config.critical,
                    passed=passed,
                    reason=reason,
                )
            )
        return results
