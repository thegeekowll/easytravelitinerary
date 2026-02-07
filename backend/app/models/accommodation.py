"""
Accommodation models for lodging and accommodation management.
"""
from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.session import Base


class AccommodationType(Base):
    """
    Accommodation Type model for categorizing accommodations.

    Examples: "Lodge", "Tented Camp", "Hotel", "Resort", "Guesthouse"
    """
    __tablename__ = "accommodation_types"

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
    accommodations: Mapped[List["Accommodation"]] = relationship(
        "Accommodation",
        back_populates="accommodation_type",
        lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<AccommodationType {self.name}>"

    def to_dict(self) -> dict:
        """Convert accommodation type to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }



class AccommodationLevel(Base):
    """
    Accommodation Level model for classifying quality/price tier.

    Examples: "Basic", "Comfort", "Comfort Plus", "Luxury", "Luxury Plus"
    """
    __tablename__ = "accommodation_levels"

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
    accommodations: Mapped[List["Accommodation"]] = relationship(
        "Accommodation",
        back_populates="accommodation_level",
        lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<AccommodationLevel {self.name}>"

    def to_dict(self) -> dict:
        """Convert accommodation level to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }

class Accommodation(Base):
    """
    Accommodation model representing lodging options.

    Stores comprehensive information about accommodations including
    amenities, room types, meal plans, and location information.
    """
    __tablename__ = "accommodations"

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

    # Type and Rating
    type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accommodation_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    level_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accommodation_levels.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    star_rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Star rating (1-5)"
    )

    # Location
    location_destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("destinations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Amenities (stored as JSON array)
    # Example: ["WiFi", "Pool", "Spa", "Restaurant", "Bar"]
    amenities: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]"
    )

    # Room Types (stored as JSON array of objects)
    # Example: [{"type": "Standard Room", "capacity": 2, "features": ["..."]}, ...]
    room_types: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]"
    )

    # Meal Plans (stored as JSON array)
    # Example: ["Full Board", "Half Board", "Bed & Breakfast", "All Inclusive"]
    meal_plans: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]"
    )

    # Additional Information
    special_features: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Missing fields added
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gps_coordinates: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    check_in_time: Mapped[str | None] = mapped_column(String(20), nullable=True)
    check_out_time: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Contact Information (stored as JSON object)
    # Example: {"email": "...", "phone": "...", "website": "...", "address": "..."}
    contact_info: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}"
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
    accommodation_type: Mapped["AccommodationType"] = relationship(
        "AccommodationType",
        back_populates="accommodations",
        lazy="joined"
    )

    accommodation_level: Mapped["AccommodationLevel"] = relationship(
        "AccommodationLevel",
        back_populates="accommodations",
        lazy="joined"
    )

    location_destination: Mapped["Destination"] = relationship(
        "Destination",
        back_populates="accommodations",
        lazy="joined"
    )

    images: Mapped[List["AccommodationImage"]] = relationship(
        "AccommodationImage",
        back_populates="accommodation",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="AccommodationImage.sort_order"
    )

    base_tour_days: Mapped[List["BaseTourDay"]] = relationship(
        "BaseTourDay",
        back_populates="accommodation",
        lazy="dynamic"
    )

    # Indexes
    __table_args__ = (
        Index("ix_accommodations_name", "name"),
        Index("ix_accommodations_type", "type_id"),
        Index("ix_accommodations_location", "location_destination_id"),
    )

    def __repr__(self) -> str:
        return f"<Accommodation {self.name}>"

    def to_dict(self) -> dict:
        """Convert accommodation to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "name": self.name,
            "description": self.description,
            "type": self.accommodation_type.name if self.accommodation_type else None,
            "level": self.accommodation_level.name if self.accommodation_level else None,
            "star_rating": self.star_rating,
            "location": self.location_destination.name if self.location_destination else None,
            "location_id": str(self.location_destination_id),
            "amenities": self.amenities,
            "room_types": self.room_types,
            "meal_plans": self.meal_plans,
            "special_features": self.special_features,
            "contact_info": self.contact_info,
            "images": [img.to_dict() for img in self.images],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class AccommodationImage(Base):
    """
    Accommodation image model for storing multiple images per accommodation.
    """
    __tablename__ = "accommodation_images"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    accommodation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accommodations.id", ondelete="CASCADE"),
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
    accommodation: Mapped["Accommodation"] = relationship(
        "Accommodation",
        back_populates="images"
    )

    # Indexes
    __table_args__ = (
        Index("ix_accommodation_images_sort", "accommodation_id", "sort_order"),
    )

    def __repr__(self) -> str:
        return f"<AccommodationImage for {self.accommodation_id}>"

    def to_dict(self) -> dict:
        """Convert accommodation image to dictionary."""
        return {
            "id": str(self.id),
            "accommodation_id": str(self.accommodation_id),
            "image_url": self.image_url,
            "caption": self.caption,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
        }
