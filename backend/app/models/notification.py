"""Notification model for user notifications."""
from datetime import datetime
import enum
import uuid

from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.db.session import Base


class NotificationTypeEnum(str, enum.Enum):
    """Notification types."""
    PAYMENT_CONFIRMED = "payment_confirmed"
    THREE_DAY_ARRIVAL = "3_day_arrival"
    ASSIGNED = "assigned"
    EDITED = "edited"
    CUSTOM = "custom"


class PriorityEnum(str, enum.Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Notification model for user notifications."""
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    itinerary_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    notification_type: Mapped[NotificationTypeEnum] = mapped_column(
        SQLEnum(NotificationTypeEnum, name="notification_type_enum"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    priority: Mapped[PriorityEnum] = mapped_column(
        SQLEnum(PriorityEnum, name="priority_enum"),
        nullable=False,
        default=PriorityEnum.MEDIUM
    )

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
        Index("ix_notifications_created", "created_at"),
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "notification_type": self.notification_type.value,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "is_read": self.is_read,
            "action_url": self.action_url,
            "created_at": self.created_at.isoformat(),
        }
