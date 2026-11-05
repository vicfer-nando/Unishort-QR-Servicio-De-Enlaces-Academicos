"""Registro estructurado en JSON sin datos personales.

El formato emite una línea JSON por evento con marca de tiempo UTC, nivel,
logger y un mensaje tratado como nombre de evento. Los campos sensibles se
eliminan o se redactan antes de serializar para respetar el principio de
privacidad del proyecto.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, TextIO

SERVICE_NAME = "unishort-qr"
REDACTED = "<redacted>"
REDACTED_URL = "<redacted-url>"

SENSITIVE_FIELDS = frozenset(
    {
        "authorization",
        "cookie",
        "cookies",
        "ip",
        "ip_address",
        "client_ip",
        "remote_addr",
        "user_agent",
        "token",
        "access_token",
        "api_key",
        "admin_api_key",
        "password",
        "secret",
        "url",
        "original_url",
        "destination_url",
        "x-admin-api-key",
        "x_admin_api_key",
    }
)

_URL_PATTERN = re.compile(r"https?://[^\s\"']+", re.IGNORECASE)
_SECRET_PATTERN = re.compile(
    r"(?i)\b(authorization|token|api[_-]?key|cookie|password|secret)\b\s*[=:]\s*(?:Bearer\s+)?\S+"
)
_PERSONAL_PATTERN = re.compile(
    r"[\w.+-]+@[\w.-]+|\b(?:\d{1,3}\.){3}\d{1,3}\b|(?<![\w:])(?:[a-fA-F0-9]{0,4}:){2,}[a-fA-F0-9:]*"
)
_STANDARD_RECORD_FIELDS = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__
) | {"message", "asctime", "taskName", "request_id"}

_request_id_context: ContextVar[Optional[str]] = ContextVar(
    "unishort_request_id", default=None
)


def set_request_id(request_id: Optional[str]) -> Token[Optional[str]]:
    """Asocia un identificador de solicitud al contexto actual.

    Parameters
    ----------
    request_id:
        Identificador recibido o generado; puede ser ``None``.

    Returns
    -------
    Token
        Testigo que permite restaurar el contexto anterior.
    """

    return _request_id_context.set(request_id)


def reset_request_id(token: Token[Optional[str]]) -> None:
    """Restaura el identificador de solicitud previo al contexto."""

    _request_id_context.reset(token)


def get_request_id() -> Optional[str]:
    """Devuelve el identificador de solicitud activo, si existe."""

    return _request_id_context.get()


def _sanitize_text(value: str) -> str:
    """Redacta URLs completas y pares clave-valor con secretos."""

    without_urls = _URL_PATTERN.sub(REDACTED_URL, value)
    without_secrets = _SECRET_PATTERN.sub(
        lambda match: f"{match.group(1)}={REDACTED}", without_urls
    )
    return _PERSONAL_PATTERN.sub(REDACTED, without_secrets)


def _sanitize_value(value: Any) -> Any:
    """Convierte un valor en una representación JSON segura."""

    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, Mapping):
        return {
            str(key): REDACTED
            if str(key).lower() in SENSITIVE_FIELDS
            else _sanitize_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize_value(item) for item in value]
    return _sanitize_text(str(value))


def _extra_fields(record: logging.LogRecord) -> Dict[str, Any]:
    """Extrae los campos adicionales permitidos de un registro."""

    fields: Dict[str, Any] = {}
    for key, value in record.__dict__.items():
        normalized = key.lower()
        if key in _STANDARD_RECORD_FIELDS or key.startswith("_"):
            continue
        if normalized in SENSITIVE_FIELDS:
            continue
        fields[str(key)] = _sanitize_value(value)
    return fields


class JsonFormatter(logging.Formatter):
    """Formateador que serializa cada registro como una línea JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Devuelve el registro como JSON con campos sensibles redactados.

        Parameters
        ----------
        record:
            Registro producido por la biblioteca ``logging``.

        Returns
        -------
        str
            Línea JSON con marca de tiempo UTC, nivel, logger y metadatos
            seguros. De las excepciones solo se conserva el nombre del tipo.
        """

        payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": SERVICE_NAME,
            "message": _sanitize_text(record.getMessage()),
        }
        request_id = getattr(record, "request_id", None) or get_request_id()
        if request_id:
            payload["request_id"] = _sanitize_text(str(request_id))
        payload.update(_extra_fields(record))
        if record.exc_info:
            # SQLAlchemy puede incluir parámetros SQL en una traza. Solo el tipo
            # de excepción es metadato seguro; no se serializa texto arbitrario.
            error_type = record.exc_info[0]
            payload["exception"] = error_type.__name__ if error_type else "Exception"
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(
    level: int | str = logging.INFO,
    stream: Optional[TextIO] = None,
    force: bool = False,
) -> None:
    """Instala un manejador JSON idempotente en el logger raíz.

    Parameters
    ----------
    level:
        Nivel mínimo de registro.
    stream:
        Flujo de salida; por defecto ``sys.stdout``.
    force:
        Si es ``True``, retira los manejadores JSON previos antes de instalar
        el nuevo. Se usa en pruebas para aislar la salida.

    Notes
    -----
    La función no toca los manejadores de Uvicorn ni imprime secretos. Llamarla
    varias veces no duplica la salida.
    """

    root = logging.getLogger()
    if force:
        for existing in list(root.handlers):
            if getattr(existing, "_unishort_json", False):
                root.removeHandler(existing)

    has_json_handler = any(
        getattr(handler, "_unishort_json", False) for handler in root.handlers
    )
    if not has_json_handler:
        handler = logging.StreamHandler(stream or sys.stdout)
        handler.setFormatter(JsonFormatter())
        setattr(handler, "_unishort_json", True)
        root.addHandler(handler)

    root.setLevel(level)
    logging.getLogger("unishort").setLevel(level)


__all__: List[str] = [
    "JsonFormatter",
    "configure_logging",
    "get_request_id",
    "reset_request_id",
    "set_request_id",
]
