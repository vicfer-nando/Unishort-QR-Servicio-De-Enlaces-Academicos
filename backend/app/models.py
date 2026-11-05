"""Modelos ORM de UniShort QR.

``ShortURL`` conserva los campos originales y añade estado, expiración y un
contador agregado de clics. No se almacenan datos personales de los visitantes.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base
from .domain import utc_now


class ShortURL(Base):
    """Enlace corto persistido.

    Attributes
    ----------
    id:
        Identificador interno.
    short_code:
        Código único que aparece en la URL corta.
    original_url:
        URL de destino completa e inmodificada.
    created_at:
        Fecha de creación en UTC.
    is_active:
        Estado administrativo del enlace.
    expires_at:
        Fecha opcional de caducidad en UTC.
    click_count:
        Contador agregado de redirecciones válidas; no guarda eventos ni datos
        personales.
    """

    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    short_code: Mapped[str] = mapped_column(
        String(16), unique=True, index=True, nullable=False
    )
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("1")
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    click_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )

    def __repr__(self) -> str:
        """Representación útil para depuración sin exponer la URL completa."""

        return f"ShortURL(short_code={self.short_code!r}, is_active={self.is_active!r})"
