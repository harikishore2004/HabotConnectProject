from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BookingRequestSchema(BaseModel):
    parent_id: int = Field(gt=0)
    lsa_id: int = Field(gt=0)
    session_date: datetime
    notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("session_date")
    @classmethod
    def session_date_must_be_future(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("session_date must include timezone info")
        now = datetime.now(v.tzinfo)
        if v <= now:
            raise ValueError("session_date must be in the future")
        return v


class BookingResponseSchema(BaseModel):
    id: int
    parent_id: int
    lsa_id: int
    session_date: str
    notes: Optional[str]
    status: str
    payment_reference: Optional[str]
    created_at: str