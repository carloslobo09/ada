from app.domain.cross_validation import ComparisonType, CrossField
from app.services.cross_validation.engine import CrossValidationEngine

CONFIG = [
    CrossField("numero_dni", ComparisonType.NUMERIC_EQUALS, critical=True, required_expected=True),
    CrossField("nombre_completo", ComparisonType.FUZZY_70, critical=True),
    CrossField("sexo", ComparisonType.EQUALS_NORMALIZED, critical=False),
]


class TestPreflight:
    def test_payload_completo_no_rechaza(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        outcome = engine.preflight({"numero_dni": "40123456"})
        assert not outcome.rejected

    def test_falta_required_rechaza(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        outcome = engine.preflight({"nombre_completo": "Carlos"})
        assert outcome.rejected
        assert outcome.missing_required == ["numero_dni"]
        assert "numero_dni" in outcome.reason()

    def test_campo_desconocido_rechaza(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        outcome = engine.preflight({"numero_dni": "40123456", "campo_inventado": "x"})
        assert outcome.rejected
        assert outcome.unknown_fields == ["campo_inventado"]

    def test_payload_vacio_rechaza_por_required(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        outcome = engine.preflight({})
        assert outcome.rejected
        assert outcome.missing_required == ["numero_dni"]


class TestEvaluate:
    def test_compara_solo_campos_enviados(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        results = engine.evaluate(
            extracted_values={
                "numero_dni": "40123456",
                "nombre_completo": "LOBO CARLOS IGNACIO",
                "sexo": "M",
            },
            expected={"numero_dni": "40.123.456"},
        )
        assert len(results) == 1
        assert results[0].field == "numero_dni"
        assert results[0].passed

    def test_ignora_campos_fuera_de_config(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        results = engine.evaluate(
            extracted_values={"numero_dni": "40123456"},
            expected={"numero_dni": "40123456", "fuera_de_config": "x"},
        )
        assert len(results) == 1
        assert results[0].field == "numero_dni"

    def test_marca_fallo(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        results = engine.evaluate(
            extracted_values={"numero_dni": "40123456"},
            expected={"numero_dni": "99999999"},
        )
        assert not results[0].passed
        assert results[0].critical
