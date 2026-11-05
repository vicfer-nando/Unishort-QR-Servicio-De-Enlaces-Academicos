"""Casos de uso de UniShort QR.

La capa de servicios orquesta validación, persistencia y composición de la
respuesta pública. No conoce detalles de FastAPI.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import repository
from .config import Settings, get_settings
from .domain import (
    build_short_url,
    is_expired,
    normalize_expiration,
    validate_destination_url,
)
from .errors import LinkExpiredError, LinkInactiveError, LinkNotFoundError
from .models import ShortURL

__all__ = ["build_short_url", "repository"]


def _iso_utc(value: Optional[datetime]) -> Optional[str]:
    """Serializa una fecha como ISO 8601 en UTC o ``None``."""

    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def link_to_data(link: ShortURL, settings: Optional[Settings] = None) -> Dict[str, Any]:
    """Convierte un enlace persistido en datos públicos de la API.

    Parameters
    ----------
    link:
        Enlace almacenado.
    settings:
        Configuración usada para construir las URL absolutas.

    Returns
    -------
    dict
        Campos del enlace listos para el envelope ``data``.
    """

    config = settings or get_settings()
    short_url = build_short_url(config.base_url, link.short_code)
    if not link.is_active:
        status = "inactive"
    elif is_expired(link.expires_at):
        status = "expired"
    else:
        status = "active"
    return {
        "short_code": link.short_code,
        "short_url": short_url,
        "original_url": link.original_url,
        "qr_url": f"{config.base_url}{config.api_prefix}/links/{link.short_code}/qr",
        "created_at": _iso_utc(link.created_at),
        "expires_at": _iso_utc(link.expires_at),
        "is_active": bool(link.is_active),
        "click_count": int(link.click_count or 0),
        "status": status,
    }


def create_short_link(
    session: Session,
    raw_url: str,
    expires_at: Optional[datetime] = None,
    settings: Optional[Settings] = None,
    code_generator: Optional[repository.CodeGenerator] = None,
) -> ShortURL:
    """Valida la entrada y crea un enlace corto persistente.

    Cada llamada genera un enlace nuevo; no se deduplica la URL original.

    Parameters
    ----------
    session:
        Sesión de base de datos.
    raw_url:
        URL recibida del cliente.
    expires_at:
        Fecha opcional de caducidad.
    settings:
        Configuración de la aplicación.
    code_generator:
        Generador alternativo para pruebas de colisión.

    Returns
    -------
    ShortURL
        Enlace persistido.

    Raises
    ------
    DomainError
        Si la URL o la expiración no son válidas, o si falla la persistencia.
    """

    config = settings or get_settings()
    original_url = validate_destination_url(raw_url, config.max_url_length)
    normalized_expiration = (
        normalize_expiration(expires_at) if expires_at is not None else None
    )
    return repository.create_link(
        session=session,
        original_url=original_url,
        expires_at=normalized_expiration,
        code_length=config.short_code_length,
        code_generator=code_generator,
    )


def get_link_or_raise(session: Session, short_code: str) -> ShortURL:
    """Recupera un enlace o lanza ``LinkNotFoundError``."""

    link = repository.get_by_code(session, short_code)
    if link is None:
        raise LinkNotFoundError
    return link


def ensure_link_usable(link: ShortURL, now: Optional[datetime] = None) -> None:
    """Comprueba que el enlace pueda redirigir.

    Raises
    ------
    LinkInactiveError
        Si el enlace está desactivado.
    LinkExpiredError
        Si la fecha de expiración ya pasó.
    """

    if not link.is_active:
        raise LinkInactiveError
    if is_expired(link.expires_at, now=now):
        raise LinkExpiredError


def resolve_link_for_redirect(session: Session, short_code: str) -> ShortURL:
    """Recupera y valida un enlace antes de emitir la redirección."""

    link = get_link_or_raise(session, short_code)
    ensure_link_usable(link)
    return link


def record_click(session: Session, short_code: str) -> None:
    """Registra un clic agregado sin interrumpir la redirección si falla."""

    try:
        repository.increment_click_count(session, short_code)
    except Exception:
        # La disponibilidad de la redirección prevalece sobre la métrica.
        return


def update_link_state(
    session: Session,
    short_code: str,
    is_active: Optional[bool] = None,
    expires_at: Optional[datetime] = None,
    update_expiration: bool = False,
) -> ShortURL:
    """Actualiza el estado administrativo de un enlace.

    Parameters
    ----------
    session:
        Sesión de base de datos.
    short_code:
        Código del enlace.
    is_active:
        Nuevo estado, si se envía.
    expires_at:
        Nueva fecha de caducidad.
    update_expiration:
        Indica si la fecha debe sobrescribirse, incluso con ``None``.

    Returns
    -------
    ShortURL
        Enlace actualizado.
    """

    link = get_link_or_raise(session, short_code)
    normalized_expiration = expires_at
    if update_expiration and expires_at is not None:
        normalized_expiration = normalize_expiration(expires_at)
    return repository.update_link(
        session=session,
        link=link,
        is_active=is_active,
        expires_at=normalized_expiration,
        update_expiration=update_expiration,
    )


def list_links(
    session: Session,
    limit: int = 50,
    offset: int = 0,
) -> tuple[List[ShortURL], int]:
    """Devuelve una página de enlaces y el total disponible."""

    return repository.list_links(
        session, limit=limit, offset=offset
    ), repository.count_links(session)


def database_is_healthy(session: Session) -> bool:
    """Comprueba la base de datos con una consulta mínima."""

    try:
        session.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False
