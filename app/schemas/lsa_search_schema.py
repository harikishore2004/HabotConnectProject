from typing import List, Optional
from pydantic import BaseModel, field_validator


class LSASearchRequestchema(BaseModel):
    skills: Optional[List[str]] = None
    is_available: Optional[bool] = None

    @field_validator("skills", mode="before")
    @classmethod
    def split_csv(cls, v):
        if v is None or isinstance(v, list):
            return v
        return [s.strip() for s in v.split(",") if s.strip()]


class LSASearchResponseSchema(BaseModel):
    id: int
    full_name: str
    email: str
    bio: Optional[str]
    is_available: bool
    hourly_rate: float
    skills: List[str]
    created_at: str