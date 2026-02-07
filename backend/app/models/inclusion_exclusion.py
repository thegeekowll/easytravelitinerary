"""
Inclusion and Exclusion models for tour packages.

These models define what is included and excluded in tour packages.
"""
from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.session import Base


class Inclusion(Base):
    """
    Inclusion model representing items included in tour packages.

    Examples: "Airport transfers", "Accommodation", "Meals", "Park fees"
    """
    __tablename__ = "inclusions"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Name of the inclusion"
    )
    icon_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Icon name for UI display (e.g., 'plane', 'hotel', 'utensils')"
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Detailed description"
    )
    image_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment="URL to an illustrative image"
    )
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Category for grouping (e.g., 'Transport', 'Accommodation', 'Meals')"
    )
    sort_order: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        comment="Order for displaying inclusions"
    )

    # Timestamps
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
    base_tours: Mapped[List["BaseTour"]] = relationship(
        "BaseTour",
        secondary="base_tour_inclusions",
        back_populates="inclusions",
        lazy="dynamic"
    )

    itineraries: Mapped[List["Itinerary"]] = relationship(
        "Itinerary",
        secondary="itinerary_inclusions",
        back_populates="inclusions",
        lazy="dynamic"
    )

    # Indexes
    __table_args__ = (
        Index("ix_inclusions_name", "name"),
        Index("ix_inclusions_category", "category"),
        Index("ix_inclusions_sort", "sort_order"),
    )

    def __repr__(self) -> str:
        return f"<Inclusion {self.name}>"

    def to_dict(self) -> dict:
        """Convert inclusion to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "icon_name": self.icon_name,
            "category": self.category,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Exclusion(Base):
    """
    Exclusion model representing items excluded from tour packages.

    Examples: "International flights", "Travel insurance", "Visa fees", "Tips"
    """
    __tablename__ = "exclusions"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Name of the exclusion"
    )
    icon_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Icon name for UI display (e.g., 'times-circle', 'ban')"
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Detailed description"
    )
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Category for grouping (e.g., 'Flights', 'Insurance', 'Personal')"
    )
    sort_order: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        comment="Order for displaying exclusions"
    )

    # Timestamps
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
    base_tours: Mapped[List["BaseTour"]] = relationship(
        "BaseTour",
        secondary="base_tour_exclusions",
        back_populates="exclusions",
        lazy="dynamic"
    )

    itineraries: Mapped[List["Itinerary"]] = relationship(
        "Itinerary",
        secondary="itinerary_exclusions",
        back_populates="exclusions",
        lazy="dynamic"
    )

    # Indexes
    __table_args__ = (
        Index("ix_exclusions_name", "name"),
        Index("ix_exclusions_category", "category"),
        Index("ix_exclusions_sort", "sort_order"),
    )

    def __repr__(self) -> str:
        return f"<Exclusion {self.name}>"

    def to_dict(self) -> dict:
        """Convert exclusion to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "icon_name": self.icon_name,
            "category": self.category,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# Common inclusion categories
class InclusionCategories:
    """Common inclusion categories."""
    TRANSPORT = "Transport"
    ACCOMMODATION = "Accommodation"
    MEALS = "Meals"
    ACTIVITIES = "Activities"
    PARK_FEES = "Park Fees"
    GUIDE_SERVICES = "Guide Services"
    OTHER = "Other"


# Common exclusion categories
class ExclusionCategories:
    """Common exclusion categories."""
    FLIGHTS = "Flights"
    INSURANCE = "Insurance"
    VISA = "Visa & Documentation"
    PERSONAL = "Personal Expenses"
    OPTIONAL_ACTIVITIES = "Optional Activities"
    OTHER = "Other"
