"""Aplicación FastAPI de UniShort QR.

Compone la API versionada ``/api/v1`` con los endpoints heredados ``/shorten`` y
``/s/{short_code}`` para no romper el frontend ni los enlaces ya publicados.
"""

import logging
from collections.abc import Awaitable, Callable
from time import perf_counter
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import models, schemas, services, utils
from .api import v1_router
from .api.deps import enforce_create_rate_limit, get_rate_limiter
from .api.envelope import error_envelope, request_language, success_envelope
from .api.schemas import ErrorEnvelope, HealthEnvelope
from .config import get_settings
from .database import Base, engine, ensure_schema, get_db
from .errors import DomainError
from .i18n import translate
from .logging_config import configure_logging, reset_request_id, set_request_id
from .rate_limit import FixedWindowRateLimiter

logger = logging.getLogger("unishort")

settings = get_settings()
configure_logging(settings.log_level)

Base.metadata.create_all(bind=engine)
ensure_schema(engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description=(
        "Servicio institucional de acortamiento de enlaces y generación de "
        "códigos QR de la Universidad Nacional de Loja. La API versionada "
        "expone /api/v1/links; /shorten y /s/{short_code} se conservan por "
        "compatibilidad."
    ),
    openapi_tags=[
        {
            "name": "links",
            "description": "Creación, consulta y administración de enlaces.",
        },
        {"name": "legacy", "description": "Endpoints conservados por compatibilidad."},
        {"name": "operaciones", "description": "Disponibilidad del servicio."},
    ],
)

_cors_origins = [
    origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
] or ["*"]
_allow_any_origin = "*" in _cors_origins

app.state.rate_limiter = FixedWindowRateLimiter(
    max_requests=settings.rate_limit_max,
    window_seconds=settings.rate_limit_window_seconds,
)


@app.middleware("http")
async def add_request_context(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Acepta o genera ``X-Request-Id``, lo propaga y registra la petición."""

    from uuid import uuid4

    server_request_id = uuid4().hex
    request_id = (request.headers.get("X-Request-Id") or server_request_id)[:128]
    request.state.request_id = request_id
    # El identificador recibido puede contener PII; solo se refleja al cliente.
    token = set_request_id(server_request_id)
    started_at = perf_counter()
    status_code = 500
    response: Response | None = None
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Log-Request-Id"] = server_request_id
        return response
    except Exception as exc:
        logger.error(
            "http_request_failed",
            extra={
                "event": "http_request_failed",
                "method": request.method,
                "path": _log_route(request),
            },
        )
        response = await unhandled_exception_handler(request, exc)
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Log-Request-Id"] = server_request_id
        return response
    finally:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        level = (
            logging.ERROR
            if status_code >= 500
            else logging.WARNING
            if status_code >= 400
            else logging.INFO
        )
        logger.log(
            level,
            "http_request_completed",
            extra={
                "event": "http_request_completed",
                "method": request.method,
                "path": _log_route(request),
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )
        reset_request_id(token)


def _log_route(request: Request) -> str:
    """Registra la plantilla de ruta sin parámetros ni rutas arbitrarias."""

    route = request.scope.get("route")
    return str(getattr(route, "path", "<unmatched>"))


def _validation_field(error: dict[str, Any]) -> str | None:
    """Extrae el nombre del campo de un error de Pydantic."""

    location = error.get("loc") or ()
    for part in reversed(location):
        if part not in ("body", "query", "path", "header"):
            return str(part)
    return None


def _validation_code(error: dict[str, Any]) -> str:
    """Traduce el tipo de error de Pydantic a un código del contrato."""

    error_type = str(error.get("type", "invalid_payload"))
    if error_type in {"url_too_long", "string_too_long"}:
        return "url_too_long"
    if error_type == "missing":
        return "invalid_payload"
    return "invalid_payload"


def _validation_message_key(error: dict[str, Any]) -> str:
    """Selecciona la clave de mensaje localizado para un error de esquema."""

    error_type = str(error.get("type", ""))
    if error_type in {"url_too_long", "string_too_long"}:
        return "url_too_long"
    if error_type == "missing" and _validation_field(error) == "url":
        return "url_required"
    return "invalid_payload"


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Convierte errores de dominio al envelope común."""

    logger.warning(
        "domain_error",
        extra={
            "event": "domain_error",
            "error_code": exc.code,
        },
    )
    language = request_language(request)
    message = translate(exc.message_key, language)
    body = error_envelope(
        request,
        [{"code": exc.code, "message": message, "field": exc.field}],
        exc.message_key,
    )
    headers: dict[str, str] = {}
    if exc.code == "rate_limit_exceeded":
        limiter = get_rate_limiter(request)
        client = request.client.host if request.client else "unknown"
        headers["Retry-After"] = str(max(1, limiter.retry_after(client)))
    return JSONResponse(status_code=exc.status_code, content=body, headers=headers)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Devuelve 422 con envelope en v1 y formato heredado en el resto."""

    if not request.url.path.startswith(settings.api_prefix):
        return JSONResponse(
            status_code=422,
            content={"detail": jsonable_encoder(exc.errors())},
        )

    language = request_language(request)
    errors = []
    for error in exc.errors():
        key = _validation_message_key(error)
        errors.append(
            {
                "code": _validation_code(error),
                "message": translate(key, language),
                "field": _validation_field(error),
            }
        )
    body = error_envelope(request, errors, "invalid_payload")
    return JSONResponse(status_code=422, content=body)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Mantiene el contrato heredado y usa envelope en ``/api/v1``."""

    if request.url.path.startswith(settings.api_prefix):
        language = request_language(request)
        detail = (
            exc.detail
            if isinstance(exc.detail, str)
            else translate("http_error", language)
        )
        body = error_envelope(
            request,
            [{"code": "http_error", "message": detail, "field": None}],
            "http_error",
        )
        return JSONResponse(
            status_code=exc.status_code, content=body, headers=exc.headers
        )
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Evita exponer trazas internas en la respuesta."""

    logger.error("unhandled_error", extra={"path": _log_route(request)})
    language = request_language(request)
    body = error_envelope(
        request,
        [
            {
                "code": "internal_error",
                "message": translate("internal_error", language),
                "field": None,
            }
        ],
        "internal_error",
    )
    return JSONResponse(status_code=500, content=body)


@app.get(
    "/health",
    tags=["operaciones"],
    response_model=HealthEnvelope,
    responses={503: {"model": ErrorEnvelope}},
)
def health_check(
    request: Request, session: Session = Depends(get_db)
) -> dict[str, Any] | JSONResponse:
    """Comprueba la disponibilidad del servicio y de la base de datos."""

    database_ok = services.database_is_healthy(session)
    data = {
        "status": "ok" if database_ok else "degraded",
        "service": "unishort-qr",
        "api_version": settings.api_version,
        "database": "ok" if database_ok else "unavailable",
    }
    if database_ok:
        return success_envelope(request, data, "health_ok", settings)
    return JSONResponse(
        status_code=503,
        content=error_envelope(
            request,
            [
                {
                    "code": "service_unavailable",
                    "message": translate("health_degraded", request_language(request)),
                    "field": None,
                }
            ],
            "health_degraded",
            settings,
        ),
    )


@app.post(
    "/shorten",
    tags=["legacy"],
    summary="Crear enlace (compatibilidad)",
    dependencies=[Depends(enforce_create_rate_limit)],
)
def shorten_url(
    request: Request, url_data: schemas.URLBase, db: Session = Depends(get_db)
) -> dict[str, str]:
    """Mantiene el contrato heredado de creación con deduplicación y código de 6."""

    try:
        original_url = str(url_data.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="URL invalida") from exc

    existing = (
        db.query(models.ShortURL)
        .filter(models.ShortURL.original_url == original_url)
        .first()
    )
    if existing:
        host = request.headers.get("host") or "localhost:8000"
        short_url = f"http://{host}/s/{existing.short_code}"
        return {
            "short_code": existing.short_code,
            "short_url": short_url,
            "original_url": original_url,
        }

    for _ in range(10):
        short_code = utils.generate_short_code(6)
        if (
            not db.query(models.ShortURL)
            .filter(models.ShortURL.short_code == short_code)
            .first()
        ):
            break
    else:
        raise HTTPException(
            status_code=500, detail="No se pudo generar un codigo unico"
        )

    db_url = models.ShortURL(short_code=short_code, original_url=original_url)
    db.add(db_url)
    try:
        db.commit()
        db.refresh(db_url)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="No se pudo guardar el enlace"
        ) from exc

    host = request.headers.get("host") or "localhost:8000"
    short_url = f"http://{host}/s/{short_code}"
    return {
        "short_code": short_code,
        "short_url": short_url,
        "original_url": original_url,
    }


@app.get("/s/{short_code}", tags=["legacy"], summary="Redirigir al destino")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    """Redirige solo enlaces activos y no caducados; no devuelve cuerpo JSON."""

    link = services.repository.get_by_code(db, short_code)
    if link is None:
        raise HTTPException(status_code=404, detail="Enlace corto no encontrado")

    services.ensure_link_usable(link)
    services.record_click(db, short_code)
    return RedirectResponse(url=link.original_url, status_code=307)


@app.get("/", tags=["legacy"])
def root() -> dict[str, str]:
    """Mensaje informativo heredado; no es un health check."""

    return {"message": "UniShort QR API", "docs": "/docs"}


app.include_router(v1_router, prefix=settings.api_prefix)

# CORS envuelve también los errores controlados por el middleware de contexto.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in _cors_origins if origin != "*"],
    allow_origin_regex=".*" if _allow_any_origin else None,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-Id", "X-Log-Request-Id"],
)
