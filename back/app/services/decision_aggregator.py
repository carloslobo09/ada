from app.domain.cross_validation import CrossValidationResult
from app.domain.decision import Decision, DecisionStatus
from app.services.rules.engine import RuleResult, Severity


def aggregate(
    rule_results: list[RuleResult],
    cross_results: list[CrossValidationResult] | None = None,
) -> Decision:
    """Calcula la decision final combinando reglas internas y validacion cruzada.

    Las reglas y validaciones cruzadas criticas determinan el estado: si alguna
    falla, el caso queda REJECTED. Si todas pasan, el caso queda APPROVED. Las
    reglas y validaciones no criticas no modifican el estado, pero quedan
    reflejadas como observaciones en el motivo cuando fallan.
    """
    cross_results = cross_results or []

    rules_critical_failed = [
        r for r in rule_results if r.severity == Severity.CRITICAL and not r.passed
    ]
    cross_critical_failed = [r for r in cross_results if r.critical and not r.passed]

    if rules_critical_failed or cross_critical_failed:
        motivos = [f"{r.name}: {r.reason}" for r in rules_critical_failed]
        motivos += [f"cross:{r.field}: {r.reason}" for r in cross_critical_failed]
        return Decision(DecisionStatus.REJECTED, " | ".join(motivos))

    rules_informative_failed = [
        r for r in rule_results if r.severity == Severity.INFORMATIVE and not r.passed
    ]
    cross_informative_failed = [r for r in cross_results if not r.critical and not r.passed]

    if rules_informative_failed or cross_informative_failed:
        observaciones = [f"{r.name}: {r.reason}" for r in rules_informative_failed]
        observaciones += [
            f"cross:{r.field}: {r.reason}" for r in cross_informative_failed
        ]
        return Decision(
            DecisionStatus.APPROVED,
            "Aprobado con observaciones. " + " | ".join(observaciones),
        )

    return Decision(
        DecisionStatus.APPROVED,
        "Todas las reglas y validaciones cruzadas pasaron correctamente.",
    )
