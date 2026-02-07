"""
Payment record model for tracking payment status.

NOTE: This is for tracking only, not processing payments.
"""
from datetime import datetime, date
from decimal import Decimal
import enum
import uuid

from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.db.session import Base


class PaymentStatusEnum(str, enum.Enum):
    """Payment status enumeration."""
    NOT_PAID = "not_paid"
    PARTIALLY_PAID = "partially_paid"
    FULLY_PAID = "fully_paid"
    CUSTOM = "custom"


class PaymentRecord(Base):
    """Payment record for tracking payment status (not processing)."""
    __tablename__ = "payment_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    payment_status: Mapped[PaymentStatusEnum] = mapped_column(
        SQLEnum(PaymentStatusEnum, name="payment_status_enum"),
        nullable=False,
        default=PaymentStatusEnum.NOT_PAID
    )

    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    payment_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(100), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="payment_records")
    created_by: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("ix_payment_records_itinerary", "itinerary_id"),
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "payment_status": self.payment_status.value,
            "total_amount": float(self.total_amount) if self.total_amount else None,
            "paid_amount": float(self.paid_amount),
            "payment_method": self.payment_method,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "created_at": self.created_at.isoformat(),
        }
