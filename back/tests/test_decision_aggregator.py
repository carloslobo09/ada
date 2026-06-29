from app.domain.decision import DecisionStatus
from app.services.decision_aggregator import aggregate
from app.services.rules.engine import RuleResult, Severity


def result(name: str, severity: Severity, passed: bool) -> RuleResult:
    return RuleResult(name=name, severity=severity, passed=passed, reason="motivo")


def test_todas_aprobadas_da_approved() -> None:
    results = [
        result("a", Severity.CRITICAL, True),
        result("b", Severity.INFORMATIVE, True),
    ]
    decision = aggregate(results)
    assert decision.status == DecisionStatus.APPROVED


def test_critica_fallada_da_rejected() -> None:
    results = [
        result("a", Severity.CRITICAL, False),
        result("b", Severity.INFORMATIVE, True),
    ]
    decision = aggregate(results)
    assert decision.status == DecisionStatus.REJECTED
    assert "a" in decision.reason


def test_solo_informativa_fallada_da_approved_con_observaciones() -> None:
    results = [
        result("critica_ok", Severity.CRITICAL, True),
        result("info_fail", Severity.INFORMATIVE, False),
    ]
    decision = aggregate(results)
    assert decision.status == DecisionStatus.APPROVED
    assert "observaciones" in decision.reason.lower()
    assert "info_fail" in decision.reason


def test_lista_vacia_da_approved() -> None:
    assert aggregate([]).status == DecisionStatus.APPROVED
