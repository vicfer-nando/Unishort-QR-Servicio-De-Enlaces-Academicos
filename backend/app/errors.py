"""Jerarquía de excepciones de dominio de UniShort QR.

Las excepciones no dependen de FastAPI ni de SQLAlchemy. La capa HTTP las
traduce a respuestas JSON con el envelope común.
"""

from typing import Optional


class DomainError(Exception):
    """Error de negocio con código estable, estado HTTP y campo asociado.

    Parameters
    ----------
    message_key:
        Clave del catálogo de mensajes usada para localizar el texto.
    field:
        Campo de entrada responsable del error, si aplica.
    """

    code = "domain_error"
    status_code = 400
    default_message_key = "invalid_request"

    def __init__(
        self,
        message_key: Optional[str] = None,
        field: Optional[str] = None,
    ) -> None:
        self.message_key = message_key or self.default_message_key
        self.field = field
        super().__init__(self.code)


class InvalidURLDomainError(DomainError):
    """La URL de destino no cumple las reglas del dominio."""

    code = "invalid_url"
    status_code = 400
    default_message_key = "invalid_url"


class EmptyURLError(DomainError):
    """La URL está vacía o compuesta solo por espacios."""

    code = "invalid_payload"
    status_code = 422
    default_message_key = "url_required"


class URLLengthError(DomainError):
    """La URL supera la longitud máxima permitida."""

    code = "url_too_long"
    status_code = 422
    default_message_key = "url_too_long"


class InvalidSchemeError(DomainError):
    """El esquema de la URL no es ``http`` ni ``https``."""

    code = "invalid_scheme"
    status_code = 400
    default_message_key = "invalid_scheme"


class InvalidHostError(DomainError):
    """La URL no tiene un host válido."""

    code = "invalid_host"
    status_code = 400
    default_message_key = "invalid_host"


class EmbeddedCredentialsError(DomainError):
    """La URL incluye credenciales embebidas."""

    code = "embedded_credentials"
    status_code = 400
    default_message_key = "embedded_credentials"


class InvalidExpirationError(DomainError):
    """La fecha de expiración no es válida."""

    code = "invalid_expiration"
    status_code = 422
    default_message_key = "invalid_expiration"


class CollisionExhaustedError(DomainError):
    """No fue posible obtener un código corto libre."""

    code = "collision_unresolved"
    status_code = 409
    default_message_key = "collision_unresolved"


class PersistenceError(DomainError):
    """Falló el guardado y la transacción fue revertida."""

    code = "persistence_failure"
    status_code = 500
    default_message_key = "persistence_failure"


class LinkNotFoundError(DomainError):
    """El código corto solicitado no existe."""

    code = "link_not_found"
    status_code = 404
    default_message_key = "link_not_found"


class LinkInactiveError(DomainError):
    """El enlace existe pero está desactivado."""

    code = "link_inactive"
    status_code = 410
    default_message_key = "link_inactive"


class LinkExpiredError(DomainError):
    """El enlace existe pero su fecha de expiración ya pasó."""

    code = "link_expired"
    status_code = 410
    default_message_key = "link_expired"


class RateLimitError(DomainError):
    """Se superó el límite de creación de enlaces."""

    code = "rate_limit_exceeded"
    status_code = 429
    default_message_key = "rate_limit_exceeded"


class AdminNotConfiguredError(DomainError):
    """No existe una clave administrativa configurada."""

    code = "admin_not_configured"
    status_code = 503
    default_message_key = "admin_not_configured"


class AdminAuthenticationRequiredError(DomainError):
    """Falta la credencial administrativa."""

    code = "admin_authentication_required"
    status_code = 401
    default_message_key = "admin_authentication_required"


class AdminForbiddenError(DomainError):
    """La credencial administrativa no es válida."""

    code = "admin_forbidden"
    status_code = 403
    default_message_key = "admin_forbidden"
