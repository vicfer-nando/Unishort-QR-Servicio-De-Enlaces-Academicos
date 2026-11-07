"""Dependencias HTTP: límite de tasa efímero y autenticación administrativa."""

import secrets
from typing import Optional

from fastapi import Request, Security
from fastapi.security import APIKeyHeader

from ..config import get_settings
from ..errors import (
    AdminAuthenticationRequiredError,
    AdminForbiddenError,
    AdminNotConfiguredError,
    RateLimitError,
)
from ..rate_limit import FixedWindowRateLimiter

admin_key_scheme = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)


def _client_key(request: Request) -> str:
    """Obtiene una clave efímera del cliente sin persistirla."""

    client = request.client
    return client.host if client and client.host else "unknown"


def get_rate_limiter(request: Request) -> FixedWindowRateLimiter:
    """Devuelve el limitador asociado a la aplicación."""

    limiter = getattr(request.app.state, "rate_limiter", None)
    if limiter is None:
        config = get_settings()
        limiter = FixedWindowRateLimiter(
            max_requests=config.rate_limit_max,
            window_seconds=config.rate_limit_window_seconds,
        )
        request.app.state.rate_limiter = limiter
    return limiter


def enforce_create_rate_limit(request: Request) -> None:
    """Aplica el límite de tasa a la creación de enlaces.

    Raises
    ------
    RateLimitError
        Si se supera el número de creaciones permitidas en la ventana.
    """

    config = get_settings()
    if not config.rate_limit_enabled:
        return

    limiter = get_rate_limiter(request)
    if limiter.check(_client_key(request)):
        return
    raise RateLimitError


def require_admin(
    request: Request,
    x_admin_api_key: Optional[str] = Security(admin_key_scheme),
) -> None:
    """Exige una clave administrativa válida en la cabecera.

    Raises
    ------
    AdminNotConfiguredError
        Si el entorno no define ``UNISHORT_ADMIN_API_KEY``.
    AdminAuthenticationRequiredError
        Si la cabecera no se envía.
    AdminForbiddenError
        Si la clave no coincide.
    """

    config = get_settings()
    request.state.admin_request = True
    if not config.admin_api_key:
        raise AdminNotConfiguredError
    if not x_admin_api_key:
        raise AdminAuthenticationRequiredError
    if not secrets.compare_digest(
        x_admin_api_key.encode("utf-8"), config.admin_api_key.encode("utf-8")
    ):
        raise AdminForbiddenError
