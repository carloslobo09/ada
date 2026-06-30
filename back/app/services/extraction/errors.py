"""Errores del puerto Extractor.

Cada adaptador (Gemini, Mock, etc.) traduce los errores de su SDK al lenguaje
del dominio. Los routers HTTP los mapean a status codes apropiados.
"""


class ExtractorError(Exception):
    """Base de los errores del puerto Extractor."""


class ExtractorUnavailableError(ExtractorError):
    """El proveedor LLM esta caido o sobrecargado (5xx upstream)."""


class ExtractorRateLimitedError(ExtractorError):
    """El proveedor LLM rechazo la solicitud por cuota o rate limit (429)."""


class ExtractorAuthError(ExtractorError):
    """Credenciales invalidas, key revocada, falta de permisos (401/403)."""


class ExtractorInvalidResponseError(ExtractorError):
    """La respuesta del modelo no se pudo parsear como el contrato esperado."""


class ExtractorTimeoutError(ExtractorError):
    """La solicitud al proveedor LLM excedio el timeout configurado."""
