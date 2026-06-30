from datetime import date

from app.domain.extraction import NormalizedExtraction
from app.services.rules.engine import Rule, RuleResult, Severity

TIPO_DOCUMENTO_REQUERIDO = "Registro Nacional de las Personas"
LONGITUD_DNI_MIN = 7
LONGITUD_DNI_MAX = 8
CONFIANZA_MINIMA = 0.7
CAMPOS_CRITICOS_CONFIANZA: tuple[str, ...] = (
    "numero_dni",
    "nombre_completo",
    "fecha_vencimiento",
    "tipo_documento",
)


def _value(target: NormalizedExtraction, key: str) -> str:
    return target.values.get(key, "")


class DniNumeroValido(Rule):
    name = "numero_dni_format"
    severity = Severity.CRITICAL

    def check(self, target: NormalizedExtraction) -> RuleResult:
        numero = _value(target, "numero_dni")
        digits = "".join(ch for ch in numero if ch.isdigit())
        if not digits:
            return RuleResult(
                self.name,
                self.severity,
                False,
                "El numero de DNI contiene caracteres no numericos o esta vacio.",
            )
        if not LONGITUD_DNI_MIN <= len(digits) <= LONGITUD_DNI_MAX:
            return RuleResult(
                self.name,
                self.severity,
                False,
                f"El numero de DNI debe tener entre {LONGITUD_DNI_MIN} y {LONGITUD_DNI_MAX} digitos.",
            )
        return RuleResult(self.name, self.severity, True, "Formato de numero de DNI valido.")


class TipoDocumentoEsDni(Rule):
    name = "tipo_documento_es_dni"
    severity = Severity.CRITICAL

    def check(self, target: NormalizedExtraction) -> RuleResult:
        tipo = _value(target, "tipo_documento")
        if TIPO_DOCUMENTO_REQUERIDO.lower() not in tipo.lower():
            return RuleResult(
                self.name,
                self.severity,
                False,
                f"El tipo de documento debe contener '{TIPO_DOCUMENTO_REQUERIDO}'.",
            )
        return RuleResult(self.name, self.severity, True, "Tipo de documento correcto.")


class DniNoVencido(Rule):
    name = "fecha_vencimiento_no_vencido"
    severity = Severity.CRITICAL

    def check(self, target: NormalizedExtraction) -> RuleResult:
        raw = _value(target, "fecha_vencimiento")
        try:
            fecha = date.fromisoformat(raw) if raw else None
        except ValueError:
            fecha = None
        if fecha is None:
            return RuleResult(
                self.name,
                self.severity,
                False,
                "No se pudo extraer la fecha de vencimiento.",
            )
        if fecha < date.today():
            return RuleResult(
                self.name,
                self.severity,
                False,
                f"El documento esta vencido (vencimiento: {fecha.isoformat()}).",
            )
        return RuleResult(self.name, self.severity, True, "El documento esta vigente.")


class ConfianzaMinima(Rule):
    name = "confianza_minima"
    severity = Severity.CRITICAL

    def check(self, target: NormalizedExtraction) -> RuleResult:
        bajos = [
            campo
            for campo in CAMPOS_CRITICOS_CONFIANZA
            if target.confidences.get(campo, 0.0) < CONFIANZA_MINIMA
        ]
        if bajos:
            return RuleResult(
                self.name,
                self.severity,
                False,
                f"Confianza insuficiente en campos criticos: {', '.join(bajos)}.",
            )
        return RuleResult(
            self.name,
            self.severity,
            True,
            "Confianza adecuada en todos los campos criticos.",
        )


class DorsoPresente(Rule):
    name = "dorso_presente"
    severity = Severity.INFORMATIVE

    def check(self, target: NormalizedExtraction) -> RuleResult:
        dorso = _value(target, "dorso_presente").upper()
        if dorso != "SI":
            return RuleResult(
                self.name,
                self.severity,
                False,
                "No se detecto el dorso del documento.",
            )
        return RuleResult(self.name, self.severity, True, "Dorso del documento presente.")


def default_dni_rules() -> list[Rule]:
    return [
        DniNumeroValido(),
        TipoDocumentoEsDni(),
        DniNoVencido(),
        ConfianzaMinima(),
        DorsoPresente(),
    ]
