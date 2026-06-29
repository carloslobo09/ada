from __future__ import annotations

import hashlib
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from app.domain.cross_validation import CrossValidationResult
from app.domain.dni import NormalizedDni
from app.models.caso import Caso
from app.repositories.caso_repo import CasoRepository
from app.repositories.decision_repo import DecisionRepository
from app.repositories.documento_repo import DocumentoRepository
from app.services.cross_validation.engine import CrossValidationEngine
from app.services.decision_aggregator import aggregate
from app.services.extraction.protocol import Extractor
from app.services.normalization import normalize_dni
from app.services.rules.engine import RuleEngine, RuleResult
from app.storage.filesystem import FilesystemStorage


class CasoService:
    """Orquesta el pipeline de procesamiento de un caso."""

    def __init__(
        self,
        caso_repository: CasoRepository,
        documento_repository: DocumentoRepository,
        decision_repository: DecisionRepository,
        storage: FilesystemStorage,
        extractor: Extractor,
        rule_engine: RuleEngine[NormalizedDni],
        cross_engine: CrossValidationEngine,
        tipo_documento_id: str,
        prompt_version_id: str,
    ) -> None:
        self._casos = caso_repository
        self._documentos = documento_repository
        self._decisiones = decision_repository
        self._storage = storage
        self._extractor = extractor
        self._rule_engine = rule_engine
        self._cross_engine = cross_engine
        self._tipo_documento_id = tipo_documento_id
        self._prompt_version_id = prompt_version_id

    def process(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str,
        expected: dict[str, str] | None = None,
        ref_usuario_cliente: str | None = None,
    ) -> Caso:
        caso = self._casos.create_recibido(ref_usuario_cliente=ref_usuario_cliente)
        documento = self._persistir_documento(caso.id, filename, content, content_type)

        if expected is not None:
            preflight = self._cross_engine.preflight(expected)
            if preflight.rejected:
                decision = self._decisiones.create(
                    veredicto="rejected",
                    motivos=preflight.reason(),
                    confianza_global=None,
                    refs_evidencias=None,
                    expected_received=expected,
                    cross_validation_results=None,
                )
                return self._casos.attach_documento_y_decision(
                    caso,
                    ref_documento=documento.id,
                    ref_decision=decision.id,
                    estado="rechazado_pre_llm",
                )

        extraction = self._extractor.extract(Path(documento.ubicacion_s3), content_type)
        normalized = normalize_dni(extraction)
        rule_results = self._rule_engine.evaluate(normalized)

        cross_results: list[CrossValidationResult] = []
        if expected:
            cross_results = self._cross_engine.evaluate(
                extracted_values_for_cross(normalized), expected
            )

        agg = aggregate(rule_results, cross_results)
        decision = self._decisiones.create(
            veredicto=agg.status.value,
            motivos=agg.reason,
            confianza_global=_confianza_global(normalized),
            refs_evidencias={
                "salida_modelo": {
                    "ref_version_prompt": self._prompt_version_id,
                    "contenido_raw": extraction.raw_response,
                },
                "resultado_extraccion": {
                    "campos_normalizados": _campos_sin_confianzas(normalized),
                    "confianza_por_campo": dict(normalized.confianzas),
                },
                "evaluacion_reglas": [rule_result_to_dict(r) for r in rule_results],
            },
            expected_received=expected,
            cross_validation_results=[cross_result_to_dict(r) for r in cross_results] or None,
        )

        return self._casos.attach_documento_y_decision(
            caso,
            ref_documento=documento.id,
            ref_decision=decision.id,
            estado="procesado",
        )

    def _persistir_documento(
        self, caso_id: str, filename: str, content: bytes, content_type: str
    ):
        ruta = self._storage.save(caso_id, filename, content)
        return self._documentos.create(
            tipo_documento_id=self._tipo_documento_id,
            ubicacion_s3=str(ruta),
            hash_integridad=hashlib.sha256(content).hexdigest(),
            content_type=content_type,
            file_size=len(content),
        )


def extracted_values_for_cross(normalized: NormalizedDni) -> dict[str, str]:
    return {
        "numero_dni": normalized.numero_dni,
        "nombre_completo": normalized.nombre_completo,
        "fecha_nacimiento": normalized.fecha_nacimiento.isoformat()
        if normalized.fecha_nacimiento
        else "",
        "fecha_emision": normalized.fecha_emision.isoformat()
        if normalized.fecha_emision
        else "",
        "fecha_vencimiento": normalized.fecha_vencimiento.isoformat()
        if normalized.fecha_vencimiento
        else "",
        "sexo": normalized.sexo,
        "nacionalidad": normalized.nacionalidad,
        "lugar_nacimiento": normalized.lugar_nacimiento,
        "numero_tramite": normalized.numero_tramite,
        "tipo_documento": normalized.tipo_documento,
        "domicilio": normalized.domicilio,
    }


def normalized_to_dict(normalized: NormalizedDni) -> dict[str, Any]:
    data = asdict(normalized)
    for key, value in list(data.items()):
        if isinstance(value, date):
            data[key] = value.isoformat()
    return data


def rule_result_to_dict(result: RuleResult) -> dict[str, Any]:
    return {
        "name": result.name,
        "severity": result.severity.value,
        "passed": result.passed,
        "reason": result.reason,
    }


def cross_result_to_dict(result: CrossValidationResult) -> dict[str, Any]:
    return {
        "field": result.field,
        "expected": result.expected,
        "extracted": result.extracted,
        "comparison": result.comparison.value,
        "critical": result.critical,
        "passed": result.passed,
        "reason": result.reason,
    }


def _campos_sin_confianzas(normalized: NormalizedDni) -> dict[str, Any]:
    data = asdict(normalized)
    campos: dict[str, Any] = {}
    for key, value in data.items():
        if key == "confianzas":
            continue
        if isinstance(value, date):
            campos[key] = value.isoformat()
        else:
            campos[key] = value
    return campos


def _confianza_global(normalized: NormalizedDni) -> float | None:
    if not normalized.confianzas:
        return None
    return min(normalized.confianzas.values())
