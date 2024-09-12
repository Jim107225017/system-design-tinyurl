from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String

from src.const import MAX_TINY_URL_LENGTH, MAX_URL_LENGTH
from src.database.base import Base


class UrlRelation(Base):
    __tablename__ = "url_relations"
    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(MAX_URL_LENGTH), nullable=False)
    tiny = Column(String(MAX_TINY_URL_LENGTH), nullable=False)
    expired_date = Column(DateTime(timezone=True), nullable=False)


class UrlCache(BaseModel):
    origin: str
    expired_date: int
