"""
Agent Type model for categorizing CS agents by expertise.
"""
from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.session import Base


class AgentType(Base):
    """
    Agent Type model for categorizing CS agents by their area of expertise.

    Examples: "Destination Expert", "Accommodation Expert", "Safari Specialist"
    """
    __tablename__ = "agent_types"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit fields
    created_by_admin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL", use_alter=True, name="fk_agent_type_created_by"),
        nullable=True,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        foreign_keys="[User.agent_type_id]",
        back_populates="agent_type",
        lazy="dynamic"
    )

    created_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_admin_id],
        lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<AgentType {self.name}>"

    @property
    def agent_count(self) -> int:
        """Get count of agents with this type."""
        return self.users.count()

    def to_dict(self) -> dict:
        """Convert agent type to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "agent_count": self.agent_count,
        }
