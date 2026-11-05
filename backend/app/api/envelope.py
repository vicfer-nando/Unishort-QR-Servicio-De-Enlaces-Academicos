"""Construcción del envelope JSON común y utilidades de petición."""

import uuid
from typing import Any, Dict, List, Optional

from fastapi import Request

from ..config import Settings, get_settings
from ..i18n import resolve_language, translate


def get_request_id(request: Request) -> str:
    """Obtiene o genera el identificador de la petición."""

    existing = getattr(request.state, "request_id", None)
    if existing:
        return str(existing)
    header_value = request.headers.get("X-Request-Id")
    if header_value and len(header_value) <= 128:
        return header_value
    generated = uuid.uuid4().hex
    request.state.request_id = generated
    return generated


def request_language(request: Request) -> str:
    """Resuelve el idioma solicitado por ``Accept-Language``."""

    return resolve_language(request.headers.get("Accept-Language"))


def response_meta(
    request: Request,
    settings: Optional[Settings] = None,
) -> Dict[str, str]:
    """Construye los metadatos comunes de una respuesta."""

    config = settings or get_settings()
    return {
        "request_id": get_request_id(request),
        "api_version": config.api_version,
        "language": request_language(request),
    }


def success_envelope(
    request: Request,
    data: Any,
    message_key: str,
    settings: Optional[Settings] = None,
) -> Dict[str, Any]:
    """Construye una respuesta exitosa con el contrato universal."""

    language = request_language(request)
    return {
        "success": True,
        "message": translate(message_key, language),
        "data": data,
        "errors": [],
        "meta": response_meta(request, settings),
    }


def error_envelope(
    request: Request,
    errors: List[Dict[str, Any]],
    message_key: str,
    settings: Optional[Settings] = None,
) -> Dict[str, Any]:
    """Construye una respuesta de error con el contrato universal."""

    language = request_language(request)
    return {
        "success": False,
        "message": translate(message_key, language),
        "data": None,
        "errors": errors,
        "meta": response_meta(request, settings),
    }
