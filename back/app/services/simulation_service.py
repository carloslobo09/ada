from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path

from app.config import Settings
from app.domain.cross_validation import CrossValidationResult
from app.schemas.simulation import SimulationOut
from app.services.caso_service import cross_result_to_dict, rule_result_to_dict
from app.services.cross_validation.engine import CrossValidationEngine
from app.services.decision_aggregator import aggregate
from app.services.extraction.factory import build_extractor
from app.services.normalization import normalize_extraction
from app.services.prompt_version_service import PromptVersionService
from app.services.rules.engine import Rule, RuleEngine
from app.services.tipo_documento_service import TipoDocumentoService


class SimulationService:
    """Ejecuta el pipeline completo contra una version de prompt arbitraria sin persistir."""

    def __init__(
        self,
        settings: Settings,
        prompt_version_service: PromptVersionService,
        tipo_documento_service: TipoDocumentoService,
        rules_resolver: Callable[[str], list[Rule]],
    ) -> None:
        self._settings = settings
        self._prompt_version_service = prompt_version_service
        self._tipo_documento_service = tipo_documento_service
        self._rules_resolver = rules_resolver

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
        tipo = self._tipo_documento_service.get(version.tipo_documento_id)
        rule_engine = RuleEngine(self._rules_resolver(tipo.nombre))

        extractor = build_extractor(
            self._settings, version.prompt_text, version.extraction_fields
        )
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

        normalized = normalize_extraction(extraction)
        rule_results = rule_engine.evaluate(normalized)

        cross_results: list[CrossValidationResult] = []
        if expected:
            cross_results = cross_engine.evaluate(normalized.values, expected)

        decision = aggregate(rule_results, cross_results)

        return SimulationOut(
            prompt_version_id=version.id,
            expected_received=expected,
            raw_extraction=normalized.raw,
            normalized_extraction=dict(normalized.values),
            rule_results=[rule_result_to_dict(r) for r in rule_results],
            cross_validation_results=[cross_result_to_dict(r) for r in cross_results] or None,
            decision_status=decision.status.value,
            decision_reason=decision.reason,
        )
