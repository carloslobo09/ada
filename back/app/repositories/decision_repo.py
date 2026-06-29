from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.decision import Decision


class DecisionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        veredicto: str,
        motivos: str,
        confianza_global: float | None,
        refs_evidencias: dict[str, Any] | None,
        expected_received: dict[str, str] | None,
        cross_validation_results: list[dict[str, Any]] | None,
    ) -> Decision:
        decision = Decision(
            veredicto=veredicto,
            motivos=motivos,
            confianza_global=confianza_global,
            refs_evidencias=refs_evidencias,
            expected_received=expected_received,
            cross_validation_results=cross_validation_results,
        )
        self._session.add(decision)
        self._session.commit()
        self._session.refresh(decision)
        return decision

    def get(self, decision_id: str) -> Decision | None:
        return self._session.get(Decision, decision_id)
