"""
Base Tour Package models for predefined tour packages.
"""
from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Integer, Boolean, Numeric, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.session import Base


# Association table for BaseTour-Inclusion many-to-many relationship
base_tour_inclusions = Table(
    "base_tour_inclusions",
    Base.metadata,
    Column(
        "base_tour_id",
        UUID(as_uuid=True),
        ForeignKey("base_tours.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "inclusion_id",
        UUID(as_uuid=True),
        ForeignKey("inclusions.id", ondelete="CASCADE"),
        primary_key=True
    )
)


# Association table for BaseTour-Exclusion many-to-many relationship
base_tour_exclusions = Table(
    "base_tour_exclusions",
    Base.metadata,
    Column(
        "base_tour_id",
        UUID(as_uuid=True),
        ForeignKey("base_tours.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "exclusion_id",
        UUID(as_uuid=True),
        ForeignKey("exclusions.id", ondelete="CASCADE"),
        primary_key=True
    )
)


# Association table for BaseTourDay-Destination many-to-many relationship
base_tour_day_destinations = Table(
    "base_tour_day_destinations",
    Base.metadata,
    Column(
        "base_tour_day_id",
        UUID(as_uuid=True),
        ForeignKey("base_tour_days.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "destination_id",
        UUID(as_uuid=True),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "sort_order",
        Integer,
        default=0,
        nullable=False
    )
)


class TourType(Base):
    """
    Tour Type model for categorizing tours.

    Examples: "Small Group Safari", "Private Safari", "Family Safari", "Honeymoon Safari"
    """
    __tablename__ = "tour_types"

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

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    base_tours: Mapped[List["BaseTour"]] = relationship(
        "BaseTour",
        back_populates="tour_type",
        lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<TourType {self.name}>"

    def to_dict(self) -> dict:
        """Convert tour type to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


class BaseTour(Base):
    """
    Base Tour Package model representing predefined tour templates.

    These are the ~200+ base tour packages that can be used as templates
    for creating customer itineraries.
    """
    __tablename__ = "base_tours"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    tour_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique tour code e.g., SSC2"
    )
    tour_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    # Tour Type
    tour_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tour_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Duration
    number_of_days: Mapped[int] = mapped_column(Integer, nullable=False)
    number_of_nights: Mapped[int] = mapped_column(Integer, nullable=False)

    # Accommodation Level
    accommodation_level_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accommodation_levels.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Images
    hero_image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Main image for the tour"
    )

    # Pricing (optional, for internal use)
    default_pricing: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Internal default pricing"
    )

    # Best Time to Travel
    best_time_to_travel: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="e.g., 'June to October'"
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # Content
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlights: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[str | None] = mapped_column(String(50), nullable=True)

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
    tour_type: Mapped["TourType"] = relationship(
        "TourType",
        back_populates="base_tours",
        lazy="joined"
    )

    accommodation_level: Mapped["AccommodationLevel"] = relationship(
        "AccommodationLevel",
        lazy="joined"
    )

    days: Mapped[List["BaseTourDay"]] = relationship(
        "BaseTourDay",
        back_populates="base_tour",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="BaseTourDay.day_number"
    )

    images: Mapped[List["BaseTourImage"]] = relationship(
        "BaseTourImage",
        back_populates="base_tour",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="BaseTourImage.sort_order"
    )

    inclusions: Mapped[List["Inclusion"]] = relationship(
        "Inclusion",
        secondary="base_tour_inclusions",
        back_populates="base_tours",
        lazy="selectin"
    )

    exclusions: Mapped[List["Exclusion"]] = relationship(
        "Exclusion",
        secondary="base_tour_exclusions",
        back_populates="base_tours",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("ix_base_tours_code", "tour_code"),
        Index("ix_base_tours_active", "is_active"),
        Index("ix_base_tours_type", "tour_type_id"),
    )

    def __repr__(self) -> str:
        return f"<BaseTour {self.tour_code}: {self.tour_name}>"

    def to_dict(self) -> dict:
        """Convert base tour to dictionary."""
        return {
            "id": str(self.id),
            "tour_code": self.tour_code,
            "tour_name": self.tour_name,
            "tour_type": self.tour_type.name if self.tour_type else None,
            "number_of_days": self.number_of_days,
            "number_of_nights": self.number_of_nights,
            "hero_image_url": self.hero_image_url,
            "default_pricing": float(self.default_pricing) if self.default_pricing else None,
            "best_time_to_travel": self.best_time_to_travel,
            "is_active": self.is_active,
            "days": [day.to_dict() for day in self.days],
            "images": [img.to_dict() for img in self.images],
            "inclusions": [inc.to_dict() for inc in self.inclusions],
            "exclusions": [exc.to_dict() for exc in self.exclusions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class BaseTourDay(Base):
    """
    Base Tour Day model representing individual days in a base tour package.
    """
    __tablename__ = "base_tour_days"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    base_tour_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("base_tours.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Day Information
    day_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Day number in the tour"
    )
    day_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Title for the day e.g., 'Arrival in Serengeti'"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Detailed description of the day"
    )
    activities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Activities for the day"
    )
    meals_included: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="e.g., 'B, L, D'"
    )

    # Accommodation
    accommodation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accommodations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Images
    atmospheric_image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Atmospheric image for the day"
    )

    # Sort Order
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Custom sort order (usually same as day_number)"
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
    base_tour: Mapped["BaseTour"] = relationship(
        "BaseTour",
        back_populates="days"
    )

    accommodation: Mapped["Accommodation"] = relationship(
        "Accommodation",
        back_populates="base_tour_days",
        lazy="joined"
    )

    destinations: Mapped[List["Destination"]] = relationship(
        "Destination",
        secondary="base_tour_day_destinations",
        back_populates="base_tour_days",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("ix_base_tour_days_tour", "base_tour_id", "day_number"),
    )

    def __repr__(self) -> str:
        return f"<BaseTourDay {self.day_number}: {self.day_title}>"

    def to_dict(self) -> dict:
        """Convert base tour day to dictionary."""
        return {
            "id": str(self.id),
            "day_number": self.day_number,
            "day_title": self.day_title,
            "description": self.description,
            "activities": self.activities,
            "accommodation": self.accommodation.name if self.accommodation else None,
            "accommodation_id": str(self.accommodation_id) if self.accommodation_id else None,
            "atmospheric_image_url": self.atmospheric_image_url,
            "destinations": [dest.name for dest in self.destinations],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class BaseTourImage(Base):
    """
    Base Tour Image model for storing multiple images per base tour.
    """
    __tablename__ = "base_tour_images"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    base_tour_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("base_tours.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Image Information
    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Azure Blob Storage URL"
    )
    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_role: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Role: cover, accommodation_end, inclusions, about_banner, end")
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    base_tour: Mapped["BaseTour"] = relationship(
        "BaseTour",
        back_populates="images"
    )

    # Indexes
    __table_args__ = (
        Index("ix_base_tour_images_sort", "base_tour_id", "sort_order"),
    )

    def __repr__(self) -> str:
        return f"<BaseTourImage for {self.base_tour_id}>"

    def to_dict(self) -> dict:
        """Convert base tour image to dictionary."""
        return {
            "id": str(self.id),
            "base_tour_id": str(self.base_tour_id),
            "image_url": self.image_url,
            "caption": self.caption,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
        }
