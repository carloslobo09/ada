from __future__ import annotations

import tempfile
from pathlib import Path

from app.config import Settings
from app.domain.cross_validation import CrossValidationResult
from app.schemas.simulation import SimulationOut
from app.services.caso_service import (
    cross_result_to_dict,
    extracted_values_for_cross,
    normalized_to_dict,
    rule_result_to_dict,
)
from app.services.cross_validation.engine import CrossValidationEngine
from app.services.decision_aggregator import aggregate
from app.services.extraction.factory import build_extractor
from app.services.normalization import normalize_dni
from app.services.prompt_version_service import PromptVersionService
from app.services.rules.engine import RuleEngine


class SimulationService:
    """Ejecuta el pipeline completo contra una version de prompt arbitraria sin persistir."""

    def __init__(
        self,
        settings: Settings,
        prompt_version_service: PromptVersionService,
        rule_engine: RuleEngine,
    ) -> None:
        self._settings = settings
        self._prompt_version_service = prompt_version_service
        self._rule_engine = rule_engine

    def simulate(
        self,
        *,
        version_id: str,
        filename: str,
        content: bytes,
        content_type: str,
        expected: dict[str, str] | None,
    ) -> SimulationOut:
        version = self._prompt_version_service.get(version_id)

        extractor = build_extractor(self._settings, version.prompt_text)
        cross_engine = CrossValidationEngine.from_config_dicts(version.cross_validation_config)

        if expected is not None:
            preflight = cross_engine.preflight(expected)
            if preflight.rejected:
                return SimulationOut(
                    prompt_version_id=version.id,
                    expected_received=expected,
                    raw_extraction=None,
                    normalized_extraction=None,
                    rule_results=None,
                    cross_validation_results=None,
                    decision_status="rejected",
                    decision_reason=preflight.reason(),
                )

        suffix = Path(filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, prefix="sim_", suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            extraction = extractor.extract(tmp_path, content_type)
        finally:
            try:
                tmp_path.unlink()
            except OSError:
                pass

        normalized = normalize_dni(extraction)
        rule_results = self._rule_engine.evaluate(normalized)

        cross_results: list[CrossValidationResult] = []
        if expected:
            extracted_values = extracted_values_for_cross(normalized)
            cross_results = cross_engine.evaluate(extracted_values, expected)

        decision = aggregate(rule_results, cross_results)

        return SimulationOut(
            prompt_version_id=version.id,
            expected_received=expected,
            raw_extraction=extraction.raw_response,
            normalized_extraction=normalized_to_dict(normalized),
            rule_results=[rule_result_to_dict(r) for r in rule_results],
            cross_validation_results=[cross_result_to_dict(r) for r in cross_results] or None,
            decision_status=decision.status.value,
            decision_reason=decision.reason,
        )
