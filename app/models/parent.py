from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import BookingRequest

class Parent(db.Model):
    """A parent who books LSA services."""
    
    __tablename__ = "parents"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    booking_requests: Mapped[list["BookingRequest"]] = relationship("BookingRequest", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Parent id={self.id} email={self.email}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

