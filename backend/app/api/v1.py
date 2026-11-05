"""Rutas REST versionadas de UniShort QR (``/api/v1``)."""

from typing import Any

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from .. import services
from ..config import get_settings
from ..database import get_db
from ..qr import generate_qr_png
from .deps import enforce_create_rate_limit, require_admin
from .envelope import success_envelope
from .schemas import (
    CreateLinkRequest,
    ErrorEnvelope,
    LinkEnvelope,
    LinkListEnvelope,
    UpdateLinkRequest,
)

router = APIRouter(
    tags=["links"],
    responses={
        code: {"model": ErrorEnvelope}
        for code in (400, 401, 403, 404, 409, 410, 422, 429, 500, 503)
    },
)


@router.post(
    "/links",
    response_model=LinkEnvelope,
    status_code=201,
    summary="Crear un enlace corto",
    responses={
        400: {"model": ErrorEnvelope, "description": "URL de dominio inválida"},
        409: {"model": ErrorEnvelope, "description": "Colisión de código no resuelta"},
        422: {"model": ErrorEnvelope, "description": "Cuerpo inválido"},
        429: {"model": ErrorEnvelope, "description": "Límite de creación superado"},
        500: {"model": ErrorEnvelope, "description": "Fallo de persistencia"},
    },
)
def create_link(
    request: Request,
    payload: CreateLinkRequest,
    session: Session = Depends(get_db),
    _: None = Depends(enforce_create_rate_limit),
) -> dict[str, Any]:
    """Crea un enlace nuevo y devuelve su código, URL corta y URL del QR."""

    link = services.create_short_link(
        session=session,
        raw_url=payload.url,
        expires_at=payload.expires_at,
    )
    settings = get_settings()
    return success_envelope(
        request,
        services.link_to_data(link, settings),
        "link_created",
        settings,
    )


@router.get(
    "/links",
    response_model=LinkListEnvelope,
    summary="Listar enlaces (administración)",
    dependencies=[Depends(require_admin)],
)
def list_links(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Lista los enlaces existentes; requiere clave administrativa."""

    links, total = services.list_links(session, limit=limit, offset=offset)
    settings = get_settings()
    return success_envelope(
        request,
        {
            "items": [services.link_to_data(link, settings) for link in links],
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        "links_listed",
        settings,
    )


@router.get(
    "/links/{short_code}",
    response_model=LinkEnvelope,
    summary="Consultar un enlace",
)
def get_link(
    request: Request,
    short_code: str,
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Devuelve los metadatos de un enlace por su código corto."""

    link = services.get_link_or_raise(session, short_code)
    settings = get_settings()
    return success_envelope(
        request,
        services.link_to_data(link, settings),
        "link_retrieved",
        settings,
    )


@router.get(
    "/links/{short_code}/stats",
    response_model=LinkEnvelope,
    summary="Consultar métricas agregadas (administración)",
    dependencies=[Depends(require_admin)],
)
def get_link_stats(
    request: Request,
    short_code: str,
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Devuelve el contador agregado de clics; no expone datos personales."""

    link = services.get_link_or_raise(session, short_code)
    settings = get_settings()
    return success_envelope(
        request,
        services.link_to_data(link, settings),
        "link_retrieved",
        settings,
    )


@router.patch(
    "/links/{short_code}",
    response_model=LinkEnvelope,
    summary="Actualizar estado o expiración (administración)",
    dependencies=[Depends(require_admin)],
)
def update_link(
    request: Request,
    short_code: str,
    payload: UpdateLinkRequest,
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Activa, desactiva o cambia la caducidad de un enlace."""

    link = services.update_link_state(
        session=session,
        short_code=short_code,
        is_active=payload.is_active,
        expires_at=payload.expires_at,
        update_expiration="expires_at" in payload.model_fields_set,
    )
    settings = get_settings()
    return success_envelope(
        request,
        services.link_to_data(link, settings),
        "link_updated",
        settings,
    )


@router.delete(
    "/links/{short_code}",
    response_model=LinkEnvelope,
    summary="Desactivar un enlace (administración)",
    dependencies=[Depends(require_admin)],
)
def deactivate_link(
    request: Request,
    short_code: str,
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Desactiva lógicamente un enlace sin borrar su registro."""

    link = services.update_link_state(
        session=session, short_code=short_code, is_active=False
    )
    settings = get_settings()
    return success_envelope(
        request,
        services.link_to_data(link, settings),
        "link_updated",
        settings,
    )


@router.get(
    "/links/{short_code}/qr",
    summary="Obtener el código QR del enlace corto",
    response_class=Response,
    responses={
        200: {"content": {"image/png": {}}, "description": "Imagen PNG del QR"},
        404: {"model": ErrorEnvelope, "description": "Enlace inexistente"},
        410: {"model": ErrorEnvelope, "description": "Enlace desactivado o caducado"},
    },
)
def get_link_qr(
    short_code: str,
    session: Session = Depends(get_db),
) -> Response:
    """Genera un PNG cuyo contenido es exactamente la URL corta."""

    link = services.resolve_link_for_redirect(session, short_code)
    settings = get_settings()
    short_url = services.build_short_url(settings.base_url, link.short_code)
    png_bytes = generate_qr_png(short_url, settings)
    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="unishort-{link.short_code}.png"',
            "Cache-Control": "no-store",
        },
    )
