"""Configuración de UniShort QR obtenida de variables de entorno.

La configuración se centraliza en :class:`Settings` para que ningún valor de
despliegue (URL base, clave administrativa o motor de datos) quede codificado
en los módulos de la aplicación.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .domain import validate_destination_url
from .errors import DomainError

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _default_database_url() -> str:
    """Devuelve la URL de SQLite usada por el proyecto existente."""

    return f"sqlite:///{(REPOSITORY_ROOT / 'unishort.db').as_posix()}"


class Settings(BaseSettings):
    """Ajustes de la aplicación con prefijo de entorno ``UNISHORT_``.

    Attributes
    ----------
    database_url:
        Cadena de conexión de SQLAlchemy. Por defecto apunta al archivo
        ``unishort.db`` de la raíz del repositorio para conservar los datos
        existentes.
    base_url:
        Dominio público usado para construir ``short_url`` y el contenido del
        código QR. No se deriva de la cabecera ``Host`` de la petición.
    admin_api_key:
        Clave provisional de administración. Si está vacía, los endpoints
        administrativos quedan deshabilitados con ``503``.
    log_level:
        Nivel mínimo del registro estructurado JSON.
    cors_origins:
        Orígenes permitidos separados por coma; ``*`` conserva el modo abierto
        del prototipo académico.
    rate_limit_max / rate_limit_window_seconds:
        Límite efímero de creación de enlaces. La clave del limitador nunca se
        persiste.
    """

    model_config = SettingsConfigDict(
        env_prefix="UNISHORT_",
        env_file=str(REPOSITORY_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "UniShort QR API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    database_url: str = Field(default_factory=_default_database_url)
    base_url: str = "http://localhost:8000"
    admin_api_key: Optional[str] = Field(default=None, repr=False)
    log_level: str = "INFO"
    cors_origins: str = "*"
    rate_limit_enabled: bool = True
    rate_limit_max: int = Field(default=60, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=60)
    short_code_length: int = Field(default=7, ge=6, le=16)
    qr_box_size: int = Field(default=10, ge=1, le=40)
    qr_border: int = Field(default=4, ge=4, le=16)
    max_url_length: int = Field(default=2048, ge=1)
    admin_list_default_limit: int = Field(default=50, ge=1, le=200)

    @field_validator("base_url")
    @classmethod
    def _normalize_base_url(cls, value: str) -> str:
        """Elimina barras finales para construir URLs cortas sin duplicarlas."""

        normalized = value.strip().rstrip("/")
        if not normalized.startswith(("http://", "https://")):
            raise ValueError("UNISHORT_BASE_URL debe comenzar con http:// o https://")
        try:
            validate_destination_url(normalized)
        except DomainError as error:
            raise ValueError(
                "UNISHORT_BASE_URL debe ser una URL absoluta sin credenciales"
            ) from error
        parsed = urlsplit(normalized)
        if parsed.query or parsed.fragment:
            raise ValueError("UNISHORT_BASE_URL no admite consulta ni fragmento")
        return normalized

    @field_validator("admin_api_key")
    @classmethod
    def _empty_key_is_none(cls, value: Optional[str]) -> Optional[str]:
        """Trata una clave vacía como ausencia de configuración."""

        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Devuelve la instancia única de configuración.

    Returns
    -------
    Settings
        Configuración cargada desde variables de entorno y ``.env``.
    """

    return Settings()
