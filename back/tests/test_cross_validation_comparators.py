from app.domain.cross_validation import ComparisonType
from app.services.cross_validation.comparators import compare


class TestEquals:
    def test_pasa_con_iguales(self) -> None:
        passed, _ = compare(ComparisonType.EQUALS, "ABC", "ABC")
        assert passed

    def test_falla_con_diferente_case(self) -> None:
        passed, _ = compare(ComparisonType.EQUALS, "abc", "ABC")
        assert not passed


class TestEqualsNormalized:
    def test_pasa_ignorando_case(self) -> None:
        passed, _ = compare(ComparisonType.EQUALS_NORMALIZED, "argentina", "ARGENTINA")
        assert passed

    def test_pasa_ignorando_acentos(self) -> None:
        passed, _ = compare(ComparisonType.EQUALS_NORMALIZED, "cordoba", "CÓRDOBA")
        assert passed

    def test_falla_con_distintos(self) -> None:
        passed, _ = compare(ComparisonType.EQUALS_NORMALIZED, "Brasil", "Argentina")
        assert not passed


class TestNumericEquals:
    def test_pasa_con_separadores(self) -> None:
        passed, _ = compare(ComparisonType.NUMERIC_EQUALS, "40.123.456", "40123456")
        assert passed

    def test_pasa_con_espacios(self) -> None:
        passed, _ = compare(ComparisonType.NUMERIC_EQUALS, "40 123 456", "40123456")
        assert passed

    def test_falla_con_distintos(self) -> None:
        passed, _ = compare(ComparisonType.NUMERIC_EQUALS, "40123457", "40123456")
        assert not passed


class TestFuzzy70:
    def test_pasa_con_pequena_variacion(self) -> None:
        passed, _ = compare(
            ComparisonType.FUZZY_70, "LOBO CARLOS IGNACIO", "Lobo Carlos Ignacio"
        )
        assert passed

    def test_pasa_con_acentos(self) -> None:
        passed, _ = compare(ComparisonType.FUZZY_70, "JOSE PEREZ", "José Pérez")
        assert passed

    def test_falla_con_distintos_nombres(self) -> None:
        passed, _ = compare(ComparisonType.FUZZY_70, "ARGENTINA", "BRASIL")
        assert not passed


class TestFuzzy60:
    def test_pasa_con_abreviatura(self) -> None:
        passed, _ = compare(
            ComparisonType.FUZZY_60,
            "AV RIVADAVIA 1234 CABA",
            "AVENIDA RIVADAVIA 1234 CABA",
        )
        assert passed


class TestContains:
    def test_pasa_cuando_expected_esta_contenido(self) -> None:
        passed, _ = compare(ComparisonType.CONTAINS, "PEREZ JUAN CARLOS", "Juan")
        assert passed

    def test_falla_cuando_no_esta(self) -> None:
        passed, _ = compare(ComparisonType.CONTAINS, "PEREZ JUAN CARLOS", "Maria")
        assert not passed
