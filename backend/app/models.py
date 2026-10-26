from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class ShortURL(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
