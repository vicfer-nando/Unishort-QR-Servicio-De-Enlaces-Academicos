"""Catálogo de mensajes en español e inglés de UniShort QR.

Los textos visibles al usuario no se incrustan en los handlers. La selección de
idioma se hace con la cabecera ``Accept-Language``.
"""

from typing import Optional

DEFAULT_LANGUAGE = "es"
SUPPORTED_LANGUAGES = ("es", "en")

MESSAGES: dict[str, dict[str, str]] = {
    "es": {
        "invalid_request": "La solicitud no es válida.",
        "invalid_payload": "El cuerpo de la solicitud no es válido.",
        "url_required": "El campo 'url' es obligatorio y no puede estar vacío.",
        "invalid_url": "La URL de destino no es válida.",
        "invalid_scheme": "Solo se admiten URLs con esquema http o https.",
        "invalid_host": "La URL debe ser absoluta y tener un host válido.",
        "embedded_credentials": "No se permiten URL con credenciales embebidas.",
        "url_too_long": "La URL supera la longitud máxima de 2048 caracteres.",
        "invalid_expiration": "La fecha de expiración debe ser futura y con zona horaria.",
        "collision_unresolved": "No se pudo generar un código corto único.",
        "persistence_failure": "No se pudo guardar el enlace. Inténtalo de nuevo.",
        "internal_error": "Ocurrió un error interno controlado.",
        "link_not_found": "Enlace corto no encontrado.",
        "link_inactive": "El enlace está desactivado.",
        "link_expired": "El enlace ha caducado.",
        "rate_limit_exceeded": "Se superó el límite de creación de enlaces. Espera un momento.",
        "admin_not_configured": "La administración no está configurada en este entorno.",
        "admin_authentication_required": "Se requiere la clave administrativa.",
        "admin_forbidden": "La clave administrativa no es válida.",
        "http_error": "La solicitud no pudo completarse.",
        "link_created": "Enlace corto creado correctamente.",
        "link_updated": "Enlace actualizado correctamente.",
        "links_listed": "Enlaces recuperados correctamente.",
        "link_retrieved": "Enlace recuperado correctamente.",
        "health_ok": "Servicio disponible.",
        "health_degraded": "Servicio disponible con la base de datos degradada.",
    },
    "en": {
        "invalid_request": "The request is not valid.",
        "invalid_payload": "The request body is not valid.",
        "url_required": "The 'url' field is required and cannot be empty.",
        "invalid_url": "The destination URL is not valid.",
        "invalid_scheme": "Only http or https URLs are allowed.",
        "invalid_host": "The URL must be absolute and have a valid host.",
        "embedded_credentials": "URLs with embedded credentials are not allowed.",
        "url_too_long": "The URL exceeds the maximum length of 2048 characters.",
        "invalid_expiration": "The expiration date must be in the future and timezone-aware.",
        "collision_unresolved": "A unique short code could not be generated.",
        "persistence_failure": "The link could not be saved. Please try again.",
        "internal_error": "A controlled internal error occurred.",
        "link_not_found": "Short link not found.",
        "link_inactive": "The link is disabled.",
        "link_expired": "The link has expired.",
        "rate_limit_exceeded": "The link creation rate limit was exceeded. Please wait.",
        "admin_not_configured": "Administration is not configured in this environment.",
        "admin_authentication_required": "The administrative key is required.",
        "admin_forbidden": "The administrative key is not valid.",
        "http_error": "The request could not be completed.",
        "link_created": "Short link created successfully.",
        "link_updated": "Link updated successfully.",
        "links_listed": "Links retrieved successfully.",
        "link_retrieved": "Link retrieved successfully.",
        "health_ok": "Service available.",
        "health_degraded": "Service available with a degraded database.",
    },
}


def resolve_language(accept_language: Optional[str]) -> str:
    """Selecciona el idioma admitido a partir de ``Accept-Language``.

    Parameters
    ----------
    accept_language:
        Valor de la cabecera HTTP. Puede ser ``None`` o una lista ponderada.

    Returns
    -------
    str
        ``"es"`` si el español aparece primero o no hay coincidencia; ``"en"``
        si el inglés es el primer idioma admitido.
    """

    if not accept_language:
        return DEFAULT_LANGUAGE
    for fragment in accept_language.split(","):
        language = fragment.split(";")[0].strip().lower()
        if language.startswith("en"):
            return "en"
        if language.startswith("es"):
            return "es"
    return DEFAULT_LANGUAGE


def translate(key: str, language: str = DEFAULT_LANGUAGE, **values: object) -> str:
    """Devuelve el mensaje localizado para ``key``.

    Parameters
    ----------
    key:
        Clave del catálogo.
    language:
        Código de idioma; si no está soportado se usa español.
    **values:
        Valores para interpolar con ``str.format``.

    Returns
    -------
    str
        Mensaje localizado. Si la clave no existe se devuelve la propia clave.
    """

    catalog = MESSAGES.get(language, MESSAGES[DEFAULT_LANGUAGE])
    template = catalog.get(key) or MESSAGES[DEFAULT_LANGUAGE].get(key, key)
    try:
        return template.format(**values)
    except (KeyError, IndexError):
        return template
