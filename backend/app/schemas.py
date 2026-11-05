from pydantic import BaseModel, ConfigDict, HttpUrl


class URLBase(BaseModel):
    url: HttpUrl


class URLInfo(URLBase):
    short_code: str
    short_url: str

    model_config = ConfigDict(from_attributes=True)
