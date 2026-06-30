from app.domain.cross_validation import ComparisonType
from app.services.cross_validation.comparators import compare


class TestEquals:
    def test_pasa_con_iguales(self) -> None:
        passed, _ = compare(ComparisonType.EQUALS, "ABC", "ABC")
        assert passed

    def test_falla_con_diferente_case(self) -> None:
        passed, _ = compare(ComparisonType.EQUALS, "abc", "ABC")
        assert not passed


class TestFuzzy70:
    def test_pasa_con_textos_similares(self) -> None:
        passed, _ = compare(
            ComparisonType.FUZZY_70, "LOBO CARLOS IGNACIO", "LOBO CARLOS IGNACIA"
        )
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
        passed, _ = compare(ComparisonType.CONTAINS, "PEREZ JUAN CARLOS", "JUAN")
        assert passed

    def test_falla_cuando_no_esta(self) -> None:
        passed, _ = compare(ComparisonType.CONTAINS, "PEREZ JUAN CARLOS", "MARIA")
        assert not passed
