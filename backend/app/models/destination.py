"""
Destination model for storing travel destinations.
"""
from datetime import datetime
from typing import List
import enum
from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.session import Base


class ImageTypeEnum(str, enum.Enum):
    """Image type enumeration for destination images."""
    ATMOSPHERIC = "atmospheric"
    ACTIVITY = "activity"
    GENERAL = "general"


class Destination(Base):
    """
    Destination model representing travel destinations.

    Stores comprehensive information about destinations including location,
    activities, best times to visit, and relationships with other destinations.
    """
    __tablename__ = "destinations"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Location Information
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    gps_latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    gps_longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)

    # Activities and Features (stored as JSON array)
    activities: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]"
    )

    # Visit Information
    best_time_to_visit: Mapped[str | None] = mapped_column(String(255), nullable=True)
    average_duration: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="e.g., '2-3 days', '1 week'"
    )
    special_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Tags for categorization and search (stored as JSON array)
    tags: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]"
    )

    # Audit Fields
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
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
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="destinations_created",
        foreign_keys=[created_by_user_id],
        lazy="joined"
    )

    images: Mapped[List["DestinationImage"]] = relationship(
        "DestinationImage",
        back_populates="destination",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="DestinationImage.sort_order"
    )

    accommodations: Mapped[List["Accommodation"]] = relationship(
        "Accommodation",
        back_populates="location_destination",
        lazy="dynamic"
    )

    # For 2D table - combinations where this destination is the first
    destination_combos_as_first: Mapped[List["DestinationCombination"]] = relationship(
        "DestinationCombination",
        foreign_keys="[DestinationCombination.destination_1_id]",
        back_populates="destination_1",
        lazy="dynamic"
    )

    # For 2D table - combinations where this destination is the second
    destination_combos_as_second: Mapped[List["DestinationCombination"]] = relationship(
        "DestinationCombination",
        foreign_keys="[DestinationCombination.destination_2_id]",
        back_populates="destination_2",
        lazy="dynamic"
    )

    # Many-to-many with BaseTourDay
    base_tour_days: Mapped[List["BaseTourDay"]] = relationship(
        "BaseTourDay",
        secondary="base_tour_day_destinations",
        back_populates="destinations",
        lazy="dynamic"
    )

    # Indexes
    __table_args__ = (
        Index("ix_destinations_name", "name"),
        Index("ix_destinations_country_region", "country", "region"),
        Index("ix_destinations_location", "gps_latitude", "gps_longitude"),
    )

    def __repr__(self) -> str:
        return f"<Destination {self.name} ({self.country})>"

    @property
    def full_location(self) -> str:
        """Get full location string."""
        if self.region:
            return f"{self.name}, {self.region}, {self.country}"
        return f"{self.name}, {self.country}"

    def to_dict(self) -> dict:
        """Convert destination to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "country": self.country,
            "region": self.region,
            "gps_latitude": float(self.gps_latitude) if self.gps_latitude else None,
            "gps_longitude": float(self.gps_longitude) if self.gps_longitude else None,
            "activities": self.activities,
            "best_time_to_visit": self.best_time_to_visit,
            "average_duration": self.average_duration,
            "special_notes": self.special_notes,
            "tags": self.tags,
            "images": [img.to_dict() for img in self.images],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class DestinationImage(Base):
    """
    Destination image model for storing multiple images per destination.

    Supports different image types: atmospheric, activity, and general.
    """
    __tablename__ = "destination_images"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Image Information
    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Azure Blob Storage URL"
    )
    image_type: Mapped[ImageTypeEnum] = mapped_column(
        SQLEnum(ImageTypeEnum, name="image_type_enum"),
        nullable=False,
        default=ImageTypeEnum.GENERAL
    )
    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        comment="Order for displaying images"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    destination: Mapped["Destination"] = relationship(
        "Destination",
        back_populates="images"
    )

    # Indexes
    __table_args__ = (
        Index("ix_destination_images_dest_type", "destination_id", "image_type"),
        Index("ix_destination_images_sort", "destination_id", "sort_order"),
    )

    def __repr__(self) -> str:
        return f"<DestinationImage {self.image_type.value} for {self.destination_id}>"

    def to_dict(self) -> dict:
        """Convert destination image to dictionary."""
        return {
            "id": str(self.id),
            "destination_id": str(self.destination_id),
            "image_url": self.image_url,
            "image_type": self.image_type.value,
            "caption": self.caption,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
        }
