from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator
from pydantic_core import PydanticCustomError

from .domain import validate_destination_url
from .errors import DomainError
from .i18n import translate


class URLBase(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def _validate_destination(cls, value: HttpUrl) -> HttpUrl:
        """Aplica también al MVP las reglas de seguridad del destino."""

        try:
            validate_destination_url(str(value))
        except DomainError as error:
            raise PydanticCustomError(
                error.code, translate(error.message_key, "es")
            ) from error
        return value


class URLInfo(URLBase):
    short_code: str
    short_url: str

    model_config = ConfigDict(from_attributes=True)
