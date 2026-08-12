import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Parent, LSAProfile


class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class BookingRequest(db.Model):

    """A booking made by a Parent for a specific LSAProfile."""

    __tablename__ = "booking_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id"), nullable=False, index=True)
    lsa_id: Mapped[int] = mapped_column(ForeignKey("lsa_profiles.id"), nullable=False, index=True)
    session_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column( Text, nullable=True)
    status: Mapped[BookingStatus] = mapped_column( Enum(BookingStatus, name="booking_status_enum"), default=BookingStatus.PENDING, nullable=False, index=True)
    payment_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column( DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    parent: Mapped["Parent"] = relationship( "Parent", back_populates="booking_requests")
    lsa: Mapped["LSAProfile"] = relationship("LSAProfile", back_populates="booking_requests")

    def __repr__(self) -> str:
        return f"<BookingRequest id={self.id} parent_id={self.parent_id} lsa_id={self.lsa_id}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "lsa_id": self.lsa_id,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "notes": self.notes,
            "status": self.status.value if self.status else None,
            "payment_reference": self.payment_reference,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }