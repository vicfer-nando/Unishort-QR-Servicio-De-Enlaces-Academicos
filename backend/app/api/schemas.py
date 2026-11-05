"""Modelos Pydantic del contrato versionado ``/api/v1``."""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CreateLinkRequest(BaseModel):
    """Cuerpo de ``POST /api/v1/links``.

    Attributes
    ----------
    url:
        URL de destino. La validación semántica se realiza en el dominio.
    expires_at:
        Fecha opcional de caducidad en formato ISO 8601.
    """

    model_config = ConfigDict(extra="forbid")

    url: str = Field(min_length=1, max_length=2048)
    expires_at: Optional[datetime] = None


class UpdateLinkRequest(BaseModel):
    """Cuerpo de ``PATCH /api/v1/links/{short_code}``."""

    model_config = ConfigDict(extra="forbid")

    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

    @model_validator(mode="after")
    def _require_at_least_one_field(self) -> "UpdateLinkRequest":
        """Impide un PATCH vacío sin campos que actualizar."""

        if not self.model_fields_set:
            raise ValueError("Debe indicarse is_active o expires_at")
        return self


class ErrorItem(BaseModel):
    """Error individual del envelope común."""

    code: str
    message: str
    field: Optional[str] = None


class ResponseMeta(BaseModel):
    """Metadatos de trazabilidad de la respuesta."""

    request_id: str
    api_version: str
    language: str = "es"


class ErrorEnvelope(BaseModel):
    """Respuesta de error real, compartida por dominio y validación HTTP."""

    success: bool = False
    message: str
    data: None = None
    errors: List[ErrorItem]
    meta: ResponseMeta


class LinkData(BaseModel):
    """Representación pública de un enlace corto."""

    short_code: str
    short_url: str
    original_url: str
    qr_url: str
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    is_active: bool = True
    click_count: int = 0
    status: str = "active"


class LinkEnvelope(BaseModel):
    """Envelope de una operación sobre un enlace."""

    success: bool
    message: str
    data: Optional[LinkData] = None
    errors: List[ErrorItem] = Field(default_factory=list)
    meta: ResponseMeta


class LinkListData(BaseModel):
    """Datos paginados de la lista de enlaces."""

    items: List[LinkData]
    total: int
    limit: int
    offset: int


class LinkListEnvelope(BaseModel):
    """Envelope de la lista administrativa de enlaces."""

    success: bool
    message: str
    data: Optional[LinkListData] = None
    errors: List[ErrorItem] = Field(default_factory=list)
    meta: ResponseMeta


class HealthEnvelope(BaseModel):
    """Envelope del endpoint de disponibilidad."""

    success: bool
    message: str
    data: Optional[dict[str, Any]] = None
    errors: List[ErrorItem] = Field(default_factory=list)
    meta: ResponseMeta
