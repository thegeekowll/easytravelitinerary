"""
Activity Log model for audit trails.
"""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.session import Base


class ActivityLog(Base):
    """
    Activity Log model for tracking user actions and system events.

    Provides an audit trail of all important actions in the system.
    """
    __tablename__ = "activity_logs"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # User Information
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Action Details
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Action performed (e.g., 'create', 'update', 'delete', 'view')"
    )
    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of entity affected (e.g., 'itinerary', 'user', 'destination')"
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the affected entity"
    )

    # Description
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Human-readable description of the action"
    )

    # Additional Data (stored as JSON)
    extra_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
        comment="Additional context data"
    )

    # Request Information
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="activity_logs",
        lazy="joined"
    )

    # Indexes
    __table_args__ = (
        Index("ix_activity_logs_user", "user_id"),
        Index("ix_activity_logs_action", "action"),
        Index("ix_activity_logs_entity", "entity_type", "entity_id"),
        Index("ix_activity_logs_created", "created_at"),
        Index("ix_activity_logs_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ActivityLog {self.action} on {self.entity_type}>"

    def to_dict(self) -> dict:
        """Convert activity log to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "user_name": self.user.full_name if self.user else None,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "description": self.description,
            "extra_data": self.extra_data,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat(),
        }


# Activity action constants
class ActivityActions:
    """Activity action constants."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
    SEND_EMAIL = "send_email"
    GENERATE_PDF = "generate_pdf"
    ASSIGN = "assign"
    UNASSIGN = "unassign"


# Entity type constants
class EntityTypes:
    """Entity type constants."""
    USER = "user"
    ITINERARY = "itinerary"
    DESTINATION = "destination"
    ACCOMMODATION = "accommodation"
    BASE_TOUR = "base_tour"
    DESTINATION_COMBINATION = "destination_combination"
    PERMISSION = "permission"
