from pydantic import BaseModel, HttpUrl


class URLBase(BaseModel):
    url: HttpUrl


class URLInfo(URLBase):
    short_code: str
    short_url: str

    class Config:
        from_attributes = True
