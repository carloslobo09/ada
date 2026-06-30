"""Registry de reglas internas por tipo documental.

Las reglas son inherentemente especificas al tipo de documento (un DNI tiene
formato distinto a una factura o un pasaporte). El registry permite agregar
nuevos tipos sin tocar el motor de reglas: se suma una entrada al mapeo con su
fabrica de reglas.

Si un tipo documental no tiene reglas registradas, el motor de reglas opera
vacio y la decision depende solo de la validacion cruzada y la confianza media
de la extraccion.
"""

from collections.abc import Callable

from app.services.rules.dni_rules import default_dni_rules
from app.services.rules.engine import Rule

RulesFactory = Callable[[], list[Rule]]

_REGISTRY: dict[str, RulesFactory] = {
    "DNI Argentino": default_dni_rules,
}


def rules_for_tipo(nombre_tipo: str) -> list[Rule]:
    factory = _REGISTRY.get(nombre_tipo)
    if factory is None:
        return []
    return factory()
