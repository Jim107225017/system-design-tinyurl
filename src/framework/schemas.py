from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, field_validator

from src.const import MAX_URL_LENGTH


class TinyUrlRequest(BaseModel):
    origin: str

    @field_validator('origin')
    def validate_url_length(cls, v: str) -> str:
        if len(str(v)) > MAX_URL_LENGTH:
            raise ValueError(f"URL Cannot Over Size {MAX_URL_LENGTH}")
        return v


class TinyUrlResponse(BaseModel):
    tiny: str
    expired_date: str
    success: bool
    reason: Optional[str] = None
    origin: str

    @field_validator('expired_date', mode='before')
    def format_expiration_date(cls, v: Union[str, datetime]) -> str:
        if isinstance(v, datetime):
            return v.date().isoformat()
        return v
