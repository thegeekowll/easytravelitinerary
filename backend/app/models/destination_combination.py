"""
Destination Combination model for 2D destination cross-reference table.

This is a CRITICAL model for auto-filling descriptions based on destination combinations.
"""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.session import Base


class DestinationCombination(Base):
    """
    Destination Combination model (2D Table).

    This table stores pre-written descriptions and activities for combinations
    of two destinations. It enables automatic content generation when creating
    itineraries with multiple destinations.

    The table supports:
    1. Single destination entries (destination_2_id is NULL)
    2. Two-destination combinations

    This is the key feature that allows CS agents to auto-fill itinerary
    descriptions based on selected destinations.
    """
    __tablename__ = "destination_combinations"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Destination References
    destination_1_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="First destination in the combination"
    )

    destination_2_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Second destination in the combination (NULL for single destination)"
    )

    # Content Fields
    description_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Auto-fill description content for this destination combination"
    )

    activity_content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Auto-fill activity content for this destination combination"
    )

    # Audit Fields
    last_edited_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
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
    destination_1: Mapped["Destination"] = relationship(
        "Destination",
        foreign_keys=[destination_1_id],
        back_populates="destination_combos_as_first",
        lazy="joined"
    )

    destination_2: Mapped["Destination"] = relationship(
        "Destination",
        foreign_keys=[destination_2_id],
        back_populates="destination_combos_as_second",
        lazy="joined"
    )

    last_edited_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[last_edited_by_user_id],
        lazy="joined"
    )

    # Indexes and Constraints
    __table_args__ = (
        # Unique constraint: a combination of two destinations should only exist once
        UniqueConstraint(
            "destination_1_id",
            "destination_2_id",
            name="uq_destination_combination"
        ),
        # Index for fast lookup by first destination
        Index("ix_dest_combo_dest1", "destination_1_id"),
        # Index for fast lookup by second destination
        Index("ix_dest_combo_dest2", "destination_2_id"),
        # Composite index for looking up combinations
        Index("ix_dest_combo_both", "destination_1_id", "destination_2_id"),
    )

    def __repr__(self) -> str:
        dest2_name = f" + {self.destination_2.name}" if self.destination_2 else ""
        return f"<DestinationCombination {self.destination_1.name}{dest2_name}>"

    @property
    def is_single_destination(self) -> bool:
        """Check if this is a single destination entry."""
        return self.destination_2_id is None

    @property
    def destination_names(self) -> str:
        """Get formatted destination names."""
        if self.is_single_destination:
            return self.destination_1.name
        return f"{self.destination_1.name} + {self.destination_2.name}"

    def to_dict(self) -> dict:
        """Convert destination combination to dictionary."""
        return {
            "id": str(self.id),
            "destination_1_id": str(self.destination_1_id),
            "destination_1_name": self.destination_1.name if self.destination_1 else None,
            "destination_2_id": str(self.destination_2_id) if self.destination_2_id else None,
            "destination_2_name": self.destination_2.name if self.destination_2 else None,
            "is_single_destination": self.is_single_destination,
            "destination_names": self.destination_names,
            "description_content": self.description_content,
            "activity_content": self.activity_content,
            "last_edited_by": self.last_edited_by.full_name if self.last_edited_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def get_combination_key(dest1_id: uuid.UUID, dest2_id: uuid.UUID | None = None) -> tuple:
        """
        Get a standardized key for looking up combinations.

        This ensures that we always look up combinations in a consistent order,
        regardless of which destination the user selected first.

        Args:
            dest1_id: First destination ID
            dest2_id: Second destination ID (optional)

        Returns:
            tuple: Standardized (dest1_id, dest2_id) tuple
        """
        if dest2_id is None:
            return (dest1_id, None)

        # Always put the smaller UUID first for consistency
        if dest1_id < dest2_id:
            return (dest1_id, dest2_id)
        else:
            return (dest2_id, dest1_id)
