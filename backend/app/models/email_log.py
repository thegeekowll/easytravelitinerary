"""Email log model for tracking sent emails."""
from datetime import datetime
import enum
import uuid

from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.db.session import Base


class DeliveryStatusEnum(str, enum.Enum):
    """Email delivery status."""
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


class EmailLog(Base):
    """Email log for tracking sent emails."""
    __tablename__ = "email_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    sent_to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    cc_emails: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    bcc_emails: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")

    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_attached: Mapped[bool] = mapped_column(Boolean, default=False)

    sent_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False
    )

    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    delivery_status: Mapped[DeliveryStatusEnum] = mapped_column(
        SQLEnum(DeliveryStatusEnum, name="delivery_status_enum"),
        nullable=False,
        default=DeliveryStatusEnum.SENT
    )

    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    clicked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="email_logs")
    sent_by: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("ix_email_logs_itinerary", "itinerary_id"),
        Index("ix_email_logs_sent_at", "sent_at"),
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "sent_to_email": self.sent_to_email,
            "subject": self.subject,
            "delivery_status": self.delivery_status.value,
            "sent_at": self.sent_at.isoformat(),
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
        }
