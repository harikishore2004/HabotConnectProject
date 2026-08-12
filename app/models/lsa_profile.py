from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import ARRAY, Boolean, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import BookingRequest


class LSAProfile(db.Model):
    """A learning support assistant service provider."""

    __tablename__ = "lsa_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    booking_requests: Mapped[list["BookingRequest"]] = relationship("BookingRequest", back_populates="lsa", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<LSAProfile id={self.id} email={self.email}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "bio": self.bio,
            "is_available": self.is_available,
            "hourly_rate": float(self.hourly_rate) if self.hourly_rate is not None else None,
            "skills": self.skills,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }