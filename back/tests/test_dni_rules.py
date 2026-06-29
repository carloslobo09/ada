from datetime import date, timedelta
from typing import Any

from app.domain.dni import NormalizedDni
from app.services.rules.dni_rules import (
    ConfianzaMinima,
    DniNoVencido,
    DniNumeroValido,
    DorsoPresente,
    TipoDocumentoEsDni,
)


def build_dni(**overrides: Any) -> NormalizedDni:
    defaults: dict[str, Any] = {
        "numero_dni": "40123456",
        "nombre_completo": "LOBO CARLOS IGNACIO",
        "fecha_nacimiento": date(1997, 8, 15),
        "fecha_emision": date(2018, 5, 20),
        "fecha_vencimiento": date.today() + timedelta(days=365),
        "sexo": "M",
        "nacionalidad": "ARGENTINA",
        "lugar_nacimiento": "BUENOS AIRES",
        "numero_tramite": "00123456789",
        "tipo_documento": "Registro Nacional de las Personas",
        "domicilio": "AV. RIVADAVIA 1234, CABA",
        "dorso_presente": True,
        "confianzas": {
            "numero_dni": 0.98,
            "nombre_completo": 0.96,
            "fecha_vencimiento": 0.96,
            "tipo_documento": 1.0,
        },
    }
    defaults.update(overrides)
    return NormalizedDni(**defaults)


class TestDniNumeroValido:
    def test_pasa_con_ocho_digitos(self) -> None:
        assert DniNumeroValido().check(build_dni()).passed

    def test_falla_con_menos_de_siete_digitos(self) -> None:
        assert not DniNumeroValido().check(build_dni(numero_dni="12345")).passed

    def test_falla_con_no_numerico(self) -> None:
        assert not DniNumeroValido().check(build_dni(numero_dni="40ABC456")).passed

    def test_falla_con_vacio(self) -> None:
        assert not DniNumeroValido().check(build_dni(numero_dni="")).passed


class TestTipoDocumentoEsDni:
    def test_pasa_con_marcador_oficial(self) -> None:
        assert TipoDocumentoEsDni().check(build_dni()).passed

    def test_pasa_case_insensitive(self) -> None:
        assert TipoDocumentoEsDni().check(
            build_dni(tipo_documento="registro nacional de las personas")
        ).passed

    def test_falla_con_otro_documento(self) -> None:
        assert not TipoDocumentoEsDni().check(build_dni(tipo_documento="Pasaporte")).passed


class TestDniNoVencido:
    def test_pasa_con_fecha_futura(self) -> None:
        assert DniNoVencido().check(build_dni()).passed

    def test_falla_con_fecha_pasada(self) -> None:
        assert not DniNoVencido().check(build_dni(fecha_vencimiento=date(2020, 1, 1))).passed

    def test_falla_sin_fecha(self) -> None:
        assert not DniNoVencido().check(build_dni(fecha_vencimiento=None)).passed


class TestConfianzaMinima:
    def test_pasa_con_todas_altas(self) -> None:
        assert ConfianzaMinima().check(build_dni()).passed

    def test_falla_con_critica_baja(self) -> None:
        bajas = {
            "numero_dni": 0.3,
            "nombre_completo": 0.95,
            "fecha_vencimiento": 0.96,
            "tipo_documento": 1.0,
        }
        assert not ConfianzaMinima().check(build_dni(confianzas=bajas)).passed


class TestDorsoPresente:
    def test_pasa_con_dorso(self) -> None:
        assert DorsoPresente().check(build_dni()).passed

    def test_falla_sin_dorso(self) -> None:
        assert not DorsoPresente().check(build_dni(dorso_presente=False)).passed
