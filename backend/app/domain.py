"""Reglas puras de dominio de UniShort QR.

Este módulo no importa FastAPI ni SQLAlchemy. Contiene la validación de la URL
de destino, la generación del código corto y el tratamiento de fechas.
"""

import secrets
from datetime import datetime, timezone
from typing import Callable, Optional
from urllib.parse import urlsplit

from .errors import (
    EmbeddedCredentialsError,
    EmptyURLError,
    InvalidExpirationError,
    InvalidHostError,
    InvalidSchemeError,
    InvalidURLDomainError,
    URLLengthError,
)

SHORT_CODE_ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"
DEFAULT_SHORT_CODE_LENGTH = 7
MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = frozenset({"http", "https"})
_CHOOSER = Callable[[str], str]


def utc_now() -> datetime:
    """Devuelve la fecha actual en UTC consciente de zona horaria."""

    return datetime.now(timezone.utc)


def generate_short_code(
    length: int = DEFAULT_SHORT_CODE_LENGTH,
    chooser: Optional[_CHOOSER] = None,
) -> str:
    """Genera un código corto con un alfabeto sin caracteres ambiguos.

    Parameters
    ----------
    length:
        Número de caracteres del código.
    chooser:
        Función usada para elegir cada carácter. Se inyecta en las pruebas para
        obtener resultados deterministas; por defecto usa ``secrets.choice``.

    Returns
    -------
    str
        Código en minúsculas compuesto por ``abcdefghijkmnpqrstuvwxyz23456789``.

    Raises
    ------
    ValueError
        Si ``length`` no es positivo.
    """

    if length < 1:
        raise ValueError("La longitud del código corto debe ser positiva")
    select = chooser or secrets.choice
    return "".join(select(SHORT_CODE_ALPHABET) for _ in range(length))


def validate_destination_url(raw_url: str, max_length: int = MAX_URL_LENGTH) -> str:
    """Valida la URL de destino y devuelve su forma almacenable.

    Solo se aceptan URL absolutas con esquema ``http`` o ``https``, host no
    vacío y sin credenciales embebidas. La URL se guarda completa, con la única
    normalización de eliminar espacios al principio y al final.

    Parameters
    ----------
    raw_url:
        Valor recibido del cliente.
    max_length:
        Longitud máxima permitida.

    Returns
    -------
    str
        URL recortada y validada.

    Raises
    ------
    EmptyURLError
        Si el valor está vacío o solo contiene espacios.
    URLLengthError
        Si supera la longitud máxima.
    InvalidURLDomainError
        Si contiene espacios internos, caracteres de control o no es absoluta.
    InvalidSchemeError
        Si el esquema no es ``http`` ni ``https``.
    InvalidHostError
        Si no hay un host válido.
    EmbeddedCredentialsError
        Si incluye usuario o contraseña.
    """

    if raw_url is None or not raw_url.strip():
        raise EmptyURLError(field="url")

    candidate = raw_url.strip()
    if len(candidate) > max_length:
        raise URLLengthError(field="url")
    if any(character.isspace() for character in candidate):
        raise InvalidURLDomainError(field="url")
    if any(ord(character) < 32 for character in candidate):
        raise InvalidURLDomainError(field="url")

    try:
        parsed = urlsplit(candidate)
    except ValueError as error:
        raise InvalidHostError(field="url") from error
    scheme = parsed.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise InvalidSchemeError(field="url")
    if not parsed.netloc or not parsed.hostname:
        raise InvalidHostError(field="url")
    if parsed.username is not None or parsed.password is not None:
        raise EmbeddedCredentialsError(field="url")
    try:
        parsed.port
    except ValueError as error:
        raise InvalidHostError(field="url") from error

    return candidate


def normalize_expiration(
    value: datetime,
    now: Optional[datetime] = None,
) -> datetime:
    """Normaliza una fecha de expiración a UTC y exige que sea futura.

    Parameters
    ----------
    value:
        Fecha recibida. Si no tiene zona horaria se asume UTC.
    now:
        Instante de referencia inyectable para las pruebas.

    Returns
    -------
    datetime
        Fecha en UTC consciente de zona horaria.

    Raises
    ------
    InvalidExpirationError
        Si la fecha no es futura.
    """

    reference = now or utc_now()
    normalized = (
        value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    )
    normalized = normalized.astimezone(timezone.utc)
    if normalized <= reference:
        raise InvalidExpirationError(field="expires_at")
    return normalized


def is_expired(expires_at: Optional[datetime], now: Optional[datetime] = None) -> bool:
    """Indica si una fecha de expiración ya se alcanzó.

    Parameters
    ----------
    expires_at:
        Fecha en UTC o ``None`` si el enlace no caduca.
    now:
        Instante de referencia inyectable para las pruebas.

    Returns
    -------
    bool
        ``True`` cuando la fecha existe y no es posterior al instante actual.
    """

    if expires_at is None:
        return False
    reference = now or utc_now()
    candidate = expires_at
    if candidate.tzinfo is None:
        candidate = candidate.replace(tzinfo=timezone.utc)
    return candidate <= reference


def build_short_url(base_url: str, short_code: str) -> str:
    """Compone la URL corta absoluta a partir de la configuración.

    Parameters
    ----------
    base_url:
        Dominio público sin barra final.
    short_code:
        Código corto emitido.

    Returns
    -------
    str
        URL corta absoluta.
    """

    return f"{base_url.rstrip('/')}/s/{short_code}"
