from app.domain.cross_validation import ComparisonType, CrossField, NormalizationType
from app.services.cross_validation.engine import CrossValidationEngine

CONFIG = [
    CrossField(
        field="numero_dni",
        normalization=[NormalizationType.DIGITS_ONLY],
        comparison=ComparisonType.EQUALS,
        critical=True,
        required_expected=True,
    ),
    CrossField(
        field="nombre_completo",
        normalization=[
            NormalizationType.TRIM,
            NormalizationType.UPPERCASE,
            NormalizationType.REMOVE_ACCENTS,
            NormalizationType.COLLAPSE_SPACES,
        ],
        comparison=ComparisonType.FUZZY_70,
        critical=True,
    ),
    CrossField(
        field="sexo",
        normalization=[NormalizationType.TRIM, NormalizationType.UPPERCASE],
        comparison=ComparisonType.EQUALS,
        critical=False,
    ),
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
    def test_dni_pasa_con_separadores_por_normalizacion(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        results = engine.evaluate(
            extracted_values={"numero_dni": "40123456"},
            expected={"numero_dni": "40.123.456"},
        )
        assert len(results) == 1
        assert results[0].passed

    def test_nombre_pasa_con_acentos_y_case(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        results = engine.evaluate(
            extracted_values={"nombre_completo": "LOBO CARLOS IGNACIO"},
            expected={"nombre_completo": "  lobo  carlos  ignácio  "},
        )
        assert len(results) == 1
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

    def test_normalization_se_propaga_al_resultado(self) -> None:
        engine = CrossValidationEngine(CONFIG)
        results = engine.evaluate(
            extracted_values={"numero_dni": "40123456"},
            expected={"numero_dni": "40123456"},
        )
        assert results[0].normalization == [NormalizationType.DIGITS_ONLY]
