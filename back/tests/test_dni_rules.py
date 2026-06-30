from datetime import date, timedelta
from typing import Any

from app.domain.extraction import NormalizedExtraction
from app.services.rules.dni_rules import (
    ConfianzaMinima,
    DniNoVencido,
    DniNumeroValido,
    DorsoPresente,
    TipoDocumentoEsDni,
)


def build_extraction(
    *,
    values: dict[str, Any] | None = None,
    confidences: dict[str, float] | None = None,
) -> NormalizedExtraction:
    base_values: dict[str, str] = {
        "numero_dni": "40123456",
        "nombre_completo": "LOBO CARLOS IGNACIO",
        "fecha_nacimiento": "1997-08-15",
        "fecha_emision": "2018-05-20",
        "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
        "sexo": "M",
        "nacionalidad": "ARGENTINA",
        "lugar_nacimiento": "BUENOS AIRES",
        "numero_tramite": "00123456789",
        "tipo_documento": "Registro Nacional de las Personas",
        "domicilio": "AV. RIVADAVIA 1234, CABA",
        "dorso_presente": "SI",
    }
    if values:
        base_values.update(values)

    base_confidences: dict[str, float] = {
        "numero_dni": 0.98,
        "nombre_completo": 0.96,
        "fecha_vencimiento": 0.96,
        "tipo_documento": 1.0,
    }
    if confidences is not None:
        base_confidences = confidences

    return NormalizedExtraction(values=base_values, confidences=base_confidences)


class TestDniNumeroValido:
    def test_pasa_con_ocho_digitos(self) -> None:
        assert DniNumeroValido().check(build_extraction()).passed

    def test_falla_con_menos_de_siete_digitos(self) -> None:
        assert not DniNumeroValido().check(
            build_extraction(values={"numero_dni": "12345"})
        ).passed

    def test_pasa_con_separadores(self) -> None:
        # La regla extrae solo digitos antes de validar largo.
        assert DniNumeroValido().check(
            build_extraction(values={"numero_dni": "40.123.456"})
        ).passed

    def test_falla_con_vacio(self) -> None:
        assert not DniNumeroValido().check(
            build_extraction(values={"numero_dni": ""})
        ).passed


class TestTipoDocumentoEsDni:
    def test_pasa_con_marcador_oficial(self) -> None:
        assert TipoDocumentoEsDni().check(build_extraction()).passed

    def test_pasa_case_insensitive(self) -> None:
        assert TipoDocumentoEsDni().check(
            build_extraction(values={"tipo_documento": "registro nacional de las personas"})
        ).passed

    def test_falla_con_otro_documento(self) -> None:
        assert not TipoDocumentoEsDni().check(
            build_extraction(values={"tipo_documento": "Pasaporte"})
        ).passed


class TestDniNoVencido:
    def test_pasa_con_fecha_futura(self) -> None:
        assert DniNoVencido().check(build_extraction()).passed

    def test_falla_con_fecha_pasada(self) -> None:
        assert not DniNoVencido().check(
            build_extraction(values={"fecha_vencimiento": "2020-01-01"})
        ).passed

    def test_falla_sin_fecha(self) -> None:
        assert not DniNoVencido().check(
            build_extraction(values={"fecha_vencimiento": ""})
        ).passed


class TestConfianzaMinima:
    def test_pasa_con_todas_altas(self) -> None:
        assert ConfianzaMinima().check(build_extraction()).passed

    def test_falla_con_critica_baja(self) -> None:
        bajas = {
            "numero_dni": 0.3,
            "nombre_completo": 0.95,
            "fecha_vencimiento": 0.96,
            "tipo_documento": 1.0,
        }
        assert not ConfianzaMinima().check(
            build_extraction(confidences=bajas)
        ).passed


class TestDorsoPresente:
    def test_pasa_con_dorso(self) -> None:
        assert DorsoPresente().check(build_extraction()).passed

    def test_falla_sin_dorso(self) -> None:
        assert not DorsoPresente().check(
            build_extraction(values={"dorso_presente": "NO"})
        ).passed
