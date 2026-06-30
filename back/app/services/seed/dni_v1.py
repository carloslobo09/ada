"""Contenido inicial de la version 1 del perfil de validacion para DNI argentino.

Se inserta en la base de datos al primer arranque si no existe ninguna version
para el tipo documental dni_argentino. Una vez insertado, las versiones
sucesivas se editan desde el panel de configuracion.
"""

DNI_PROMPT_V1 = """Actuá como un auditor documental experto en el análisis de Documentos
Nacionales de Identidad de la República Argentina. Vas a recibir una imagen
escaneada o fotografía digital del documento. Tu tarea es extraer los campos
definidos en el esquema de salida de manera literal, sin interpretar, sin
inferir y sin completar información que no esté visible. La validación de
coherencia de los datos extraídos no es responsabilidad tuya: se ejecuta en
una etapa posterior del sistema mediante reglas determinísticas.

Para cada campo devolvé un objeto con tres atributos: value con el valor
extraído como string, confidence con un número entre cero y uno, y status
con uno de los valores approved o rejected.

Reglas de extracción:
- numero_dni: solo dígitos, sin puntos, guiones ni espacios.
- nombre_completo: apellidos primero, luego nombres, en mayúsculas, tal como
  aparecen impresos.
- fecha_nacimiento, fecha_emision y fecha_vencimiento: formato ISO yyyy-mm-dd.
  Para meses de tres letras usar la whitelist: ENE/JAN=01, FEB=02, MAR=03,
  ABR/APR=04, MAY=05, JUN=06, JUL=07, AGO/AUG=08, SEP/SET=09, OCT=10, NOV=11,
  DIC/DEC=12. Nunca adivinar; si el token es ambiguo, devolver value vacío
  con status rejected y confidence cero.
- sexo: única letra M o F.
- nacionalidad: texto literal del campo.
- lugar_nacimiento: ciudad o provincia tal como figura en el documento, en
  mayúsculas.
- numero_tramite: tal como aparece, sin separadores.
- tipo_documento: si están presentes los marcadores "Registro Nacional de
  las Personas" o "Ministerio del Interior", value = "Registro Nacional de
  las Personas" y status = approved. Caso contrario, value vacío y status
  rejected.
- domicilio: domicilio del titular tal como figura en el dorso, en una sola
  línea, en mayúsculas. Si no hay dorso o no se observa el campo, value vacío
  y status rejected.
- dorso_presente: SI si se observan palabras como pulgar, huella dactilar,
  domicilio o autoridad emisora en la imagen; NO en caso contrario.

Si un campo no es legible o no está presente, devolvé value vacío,
confidence cero y status rejected. Nunca inventes valores plausibles.
"""

DNI_EXTRACTION_FIELDS_V1: list[dict] = [
    {"name": "numero_dni", "label": "Numero de DNI"},
    {"name": "nombre_completo", "label": "Nombre completo"},
    {"name": "fecha_nacimiento", "label": "Fecha de nacimiento"},
    {"name": "fecha_emision", "label": "Fecha de emision"},
    {"name": "fecha_vencimiento", "label": "Fecha de vencimiento"},
    {"name": "sexo", "label": "Sexo"},
    {"name": "nacionalidad", "label": "Nacionalidad"},
    {"name": "lugar_nacimiento", "label": "Lugar de nacimiento"},
    {"name": "numero_tramite", "label": "Numero de tramite"},
    {"name": "tipo_documento", "label": "Tipo de documento"},
    {"name": "domicilio", "label": "Domicilio"},
    {"name": "dorso_presente", "label": "Dorso presente"},
]

DNI_CROSS_VALIDATION_CONFIG_V1: list[dict] = [
    {
        "field": "numero_dni",
        "normalization": ["digits_only"],
        "comparison": "equals",
        "critical": True,
        "required_expected": True,
    },
    {
        "field": "nombre_completo",
        "normalization": ["trim", "uppercase", "remove_accents", "collapse_spaces"],
        "comparison": "fuzzy_70",
        "critical": True,
        "required_expected": False,
    },
    {
        "field": "fecha_nacimiento",
        "normalization": ["trim"],
        "comparison": "equals",
        "critical": True,
        "required_expected": False,
    },
    {
        "field": "sexo",
        "normalization": ["trim", "uppercase"],
        "comparison": "equals",
        "critical": False,
        "required_expected": False,
    },
    {
        "field": "nacionalidad",
        "normalization": ["trim", "uppercase", "remove_accents"],
        "comparison": "equals",
        "critical": False,
        "required_expected": False,
    },
    {
        "field": "lugar_nacimiento",
        "normalization": ["trim", "uppercase", "remove_accents", "collapse_spaces"],
        "comparison": "fuzzy_70",
        "critical": False,
        "required_expected": False,
    },
    {
        "field": "domicilio",
        "normalization": ["trim", "uppercase", "remove_accents", "collapse_spaces"],
        "comparison": "fuzzy_60",
        "critical": False,
        "required_expected": False,
    },
]
