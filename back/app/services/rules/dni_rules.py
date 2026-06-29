from datetime import date

from app.domain.dni import NormalizedDni
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


class DniNumeroValido(Rule[NormalizedDni]):
    name = "numero_dni_format"
    severity = Severity.CRITICAL

    def check(self, target: NormalizedDni) -> RuleResult:
        numero = target.numero_dni
        if not numero or not numero.isdigit():
            return RuleResult(
                self.name,
                self.severity,
                False,
                "El numero de DNI contiene caracteres no numericos o esta vacio.",
            )
        if not LONGITUD_DNI_MIN <= len(numero) <= LONGITUD_DNI_MAX:
            return RuleResult(
                self.name,
                self.severity,
                False,
                f"El numero de DNI debe tener entre {LONGITUD_DNI_MIN} y {LONGITUD_DNI_MAX} digitos.",
            )
        return RuleResult(self.name, self.severity, True, "Formato de numero de DNI valido.")


class TipoDocumentoEsDni(Rule[NormalizedDni]):
    name = "tipo_documento_es_dni"
    severity = Severity.CRITICAL

    def check(self, target: NormalizedDni) -> RuleResult:
        if TIPO_DOCUMENTO_REQUERIDO.lower() not in target.tipo_documento.lower():
            return RuleResult(
                self.name,
                self.severity,
                False,
                f"El tipo de documento debe contener '{TIPO_DOCUMENTO_REQUERIDO}'.",
            )
        return RuleResult(self.name, self.severity, True, "Tipo de documento correcto.")


class DniNoVencido(Rule[NormalizedDni]):
    name = "fecha_vencimiento_no_vencido"
    severity = Severity.CRITICAL

    def check(self, target: NormalizedDni) -> RuleResult:
        if target.fecha_vencimiento is None:
            return RuleResult(
                self.name,
                self.severity,
                False,
                "No se pudo extraer la fecha de vencimiento.",
            )
        if target.fecha_vencimiento < date.today():
            return RuleResult(
                self.name,
                self.severity,
                False,
                f"El documento esta vencido (vencimiento: {target.fecha_vencimiento.isoformat()}).",
            )
        return RuleResult(self.name, self.severity, True, "El documento esta vigente.")


class ConfianzaMinima(Rule[NormalizedDni]):
    name = "confianza_minima"
    severity = Severity.CRITICAL

    def check(self, target: NormalizedDni) -> RuleResult:
        bajos = [
            campo
            for campo in CAMPOS_CRITICOS_CONFIANZA
            if target.confianzas.get(campo, 0.0) < CONFIANZA_MINIMA
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


class DorsoPresente(Rule[NormalizedDni]):
    name = "dorso_presente"
    severity = Severity.INFORMATIVE

    def check(self, target: NormalizedDni) -> RuleResult:
        if not target.dorso_presente:
            return RuleResult(
                self.name,
                self.severity,
                False,
                "No se detecto el dorso del documento.",
            )
        return RuleResult(self.name, self.severity, True, "Dorso del documento presente.")


def default_dni_rules() -> list[Rule[NormalizedDni]]:
    return [
        DniNumeroValido(),
        TipoDocumentoEsDni(),
        DniNoVencido(),
        ConfianzaMinima(),
        DorsoPresente(),
    ]
