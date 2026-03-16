"""
Itinerary models for customer itineraries.

This is the core of the application - where CS agents create and manage
customer itineraries.
"""
from datetime import datetime, date, timedelta
from typing import List
from decimal import Decimal
import enum
import secrets
import string
from sqlalchemy import (
    String, DateTime, Text, ForeignKey, Index, Integer,
    Boolean, Numeric, Date, CheckConstraint, Table, Column,
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.session import Base


# Enums
class ItineraryStatusEnum(str, enum.Enum):
    """Itinerary status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    UNDER_REVIEW = "under_review"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CreationMethodEnum(str, enum.Enum):
    """Itinerary creation method enumeration."""
    CHOOSE_EXISTING = "choose_existing"  # Created from base tour
    EDIT_EXISTING = "edit_existing"      # Edited from base tour
    CUSTOM = "custom"                    # Fully custom


class PaymentStatusEnum(str, enum.Enum):
    """Payment status enumeration."""
    NOT_PAID = "not_paid"
    PARTIALLY_PAID = "partially_paid"
    FULLY_PAID = "fully_paid"
    CUSTOM = "custom"


class DeliveryStatusEnum(str, enum.Enum):
    """Email delivery status enumeration."""
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"





class NotificationTypeEnum(str, enum.Enum):
    """Notification type enumeration."""
    PAYMENT_CONFIRMED = "payment_confirmed"
    THREE_DAY_ARRIVAL = "3_day_arrival"
    ASSIGNED = "assigned"
    EDITED = "edited"
    CUSTOM = "custom"


class PriorityEnum(str, enum.Enum):
    """Notification priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AssetTypeEnum(str, enum.Enum):
    """Company asset type enumeration."""
    LOGO = "logo"
    AWARD_BADGE = "award_badge"
    CERTIFICATION = "certification"


# Association tables
itinerary_day_destinations = Table(
    "itinerary_day_destinations",
    Base.metadata,
    Column(
        "itinerary_day_id",
        UUID(as_uuid=True),
        ForeignKey("itinerary_days.id", ondelete="CASCADE"),
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

itinerary_featured_accommodations = Table(
    "itinerary_featured_accommodations",
    Base.metadata,
    Column(
        "itinerary_id",
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "accommodation_id",
        UUID(as_uuid=True),
        ForeignKey("accommodations.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "sort_order",
        Integer,
        default=0,
        nullable=False
    )
)

itinerary_inclusions = Table(
    "itinerary_inclusions",
    Base.metadata,
    Column(
        "itinerary_id",
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "inclusion_id",
        UUID(as_uuid=True),
        ForeignKey("inclusions.id", ondelete="CASCADE"),
        primary_key=True
    )
)

itinerary_exclusions = Table(
    "itinerary_exclusions",
    Base.metadata,
    Column(
        "itinerary_id",
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "exclusion_id",
        UUID(as_uuid=True),
        ForeignKey("exclusions.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Itinerary(Base):
    """
    Itinerary model representing customer itineraries.

    This is the core entity of the application. CS agents create itineraries
    for customers, either from base tour packages or custom builds.
    """
    __tablename__ = "itineraries"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    unique_code: Mapped[str] = mapped_column(
        String(12),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique code for public URL (e.g., ABC123XYZ456)"
    )

    # Tour Information
    tour_title: Mapped[str] = mapped_column(String(255), nullable=False)
    tour_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Can be same as base tour or custom"
    )

    tour_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tour_types.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    accommodation_level_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accommodation_levels.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    difficulty_level: Mapped[str | None] = mapped_column(
        String(50), 
        nullable=True,
        comment="e.g. Easy, Moderate, Challenging"
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlights: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Duration (auto-calculated from days)
    number_of_days: Mapped[int] = mapped_column(Integer, nullable=False)
    number_of_nights: Mapped[int] = mapped_column(Integer, nullable=False)
    number_of_travelers: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Pricing
    total_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, default=0)
    deposit_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Images
    hero_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Travel Dates
    departure_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    return_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Status
    status: Mapped[ItineraryStatusEnum] = mapped_column(
        SQLEnum(ItineraryStatusEnum, name="itinerary_status_enum"),
        nullable=False,
        default=ItineraryStatusEnum.DRAFT,
        index=True
    )

    payment_status: Mapped[PaymentStatusEnum] = mapped_column(
        String(50),
        nullable=False,
        default=PaymentStatusEnum.NOT_PAID
    )
    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Marks if itinerary is fully built and ready"
    )

    # Creation Information
    created_from_base_tour_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("base_tours.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="If created from base tour, track which one"
    )

    creation_method: Mapped[CreationMethodEnum] = mapped_column(
        SQLEnum(CreationMethodEnum, name="creation_method_enum"),
        nullable=False,
        default=CreationMethodEnum.CUSTOM
    )

    # User Assignment
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True
    )

    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
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
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # PDF Generation
    pdf_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="URL of generated PDF document"
    )
    pdf_generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When PDF was last generated"
    )

    # Internal Notes
    internal_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Internal notes for CS agents, not visible to customers"
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # Edit Control
    can_edit_after_tour: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Only admin can edit after tour ends unless this is True"
    )

    # Relationships
    tour_type: Mapped["TourType"] = relationship(
        "TourType",
        lazy="joined"
    )

    accommodation_level: Mapped["AccommodationLevel"] = relationship(
        "AccommodationLevel",
        lazy="joined"
    )

    created_from_base_tour: Mapped["BaseTour"] = relationship(
        "BaseTour",
        foreign_keys=[created_from_base_tour_id],
        lazy="joined"
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="itineraries_created",
        lazy="joined"
    )

    assigned_agent: Mapped["User"] = relationship(
        "User",
        foreign_keys=[assigned_to_user_id],
        back_populates="itineraries_assigned",
        lazy="joined"
    )

    days: Mapped[List["ItineraryDay"]] = relationship(
        "ItineraryDay",
        back_populates="itinerary",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ItineraryDay.day_number"
    )

    travelers: Mapped[List["Traveler"]] = relationship(
        "Traveler",
        back_populates="itinerary",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    featured_accommodations: Mapped[List["Accommodation"]] = relationship(
        "Accommodation",
        secondary="itinerary_featured_accommodations",
        lazy="selectin"
    )

    inclusions: Mapped[List["Inclusion"]] = relationship(
        "Inclusion",
        secondary="itinerary_inclusions",
        back_populates="itineraries",
        lazy="selectin"
    )

    exclusions: Mapped[List["Exclusion"]] = relationship(
        "Exclusion",
        secondary="itinerary_exclusions",
        back_populates="itineraries",
        lazy="selectin"
    )

    payment_records: Mapped[List["PaymentRecord"]] = relationship(
        "PaymentRecord",
        back_populates="itinerary",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    email_logs: Mapped[List["EmailLog"]] = relationship(
        "EmailLog",
        back_populates="itinerary",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )



    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="itinerary",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    images: Mapped[List["ItineraryImage"]] = relationship(
        "ItineraryImage",
        back_populates="itinerary",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ItineraryImage.sort_order"
    )

    # Indexes and Constraints
    __table_args__ = (
        CheckConstraint("number_of_days > 0", name="check_positive_days"),
        CheckConstraint("number_of_nights >= 0", name="check_non_negative_nights"),
        CheckConstraint("return_date >= departure_date", name="check_valid_date_range"),
        Index("ix_itineraries_status", "status"),
        Index("ix_itineraries_departure_date", "departure_date"),
        Index("ix_itineraries_created_by", "created_by_user_id"),
        Index("ix_itineraries_assigned_to", "assigned_to_user_id"),
        Index("ix_itineraries_is_deleted", "is_deleted"),
        Index("ix_itineraries_unique_code", "unique_code"),
    )

    def __repr__(self) -> str:
        return f"<Itinerary {self.unique_code}: {self.tour_title}>"

    @staticmethod
    def generate_unique_code() -> str:
        """
        Generate a unique 12-character alphanumeric code for public URLs.

        Format: ABC123XYZ456 (uppercase letters and numbers only)

        Returns:
            str: Unique 12-character code
        """
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(12))

    def get_public_url(self, base_url: str = "https://example.com") -> str:
        """
        Get the public URL for viewing this itinerary.

        Args:
            base_url: Base URL of the application

        Returns:
            str: Full public URL
        """
        return f"{base_url}/itinerary/{self.unique_code}"

    def is_editable(self, user_role: str) -> bool:
        """
        Check if itinerary is editable based on tour dates and user role.

        Rules:
        - Always editable if tour hasn't ended
        - After tour ends: only editable if can_edit_after_tour=True OR user is admin

        Args:
            user_role: User role ('admin' or 'cs_agent')

        Returns:
            bool: True if editable, False otherwise
        """
        # Soft deleted itineraries are not editable
        if self.is_deleted:
            return False

        # If tour hasn't ended yet, always editable
        if self.return_date >= date.today():
            return True

        # Tour has ended
        # Admin can always edit OR if can_edit_after_tour is True
        return user_role == "admin" or self.can_edit_after_tour

    def auto_calculate_dates(self) -> None:
        """
        Auto-calculate number_of_days, number_of_nights, and return_date.

        Call this after setting departure_date and number_of_days.
        """
        if self.departure_date and self.number_of_days:
            self.return_date = self.departure_date + timedelta(days=self.number_of_days - 1)
            self.number_of_nights = self.number_of_days - 1

    @property
    def primary_traveler(self) -> "Traveler | None":
        """Get the primary traveler for this itinerary."""
        for traveler in self.travelers:
            if traveler.is_primary:
                return traveler
        return None

    @property
    def client_name(self) -> str:
        """Get client name from primary traveler."""
        return self.primary_traveler.full_name if self.primary_traveler else "Guest"

    @client_name.setter
    def client_name(self, value: str) -> None:
        """Set client name on primary traveler."""
        if self.primary_traveler:
            self.primary_traveler.full_name = value

    @property
    def client_email(self) -> str:
        """Get client email from primary traveler."""
        return self.primary_traveler.email if self.primary_traveler and self.primary_traveler.email else "guest@example.com"

    @client_email.setter
    def client_email(self, value: str) -> None:
        """Set client email on primary traveler."""
        if self.primary_traveler:
            self.primary_traveler.email = value

    @property
    def client_phone(self) -> str | None:
        """Get client phone from primary traveler."""
        return self.primary_traveler.phone if self.primary_traveler else None

    @client_phone.setter
    def client_phone(self, value: str | None) -> None:
        """Set client phone on primary traveler."""
        if self.primary_traveler:
            self.primary_traveler.phone = value

    @property
    def duration_days(self) -> int:
        """Alias for number_of_days to match schema."""
        return self.number_of_days

    @property
    def duration_nights(self) -> int:
        """Alias for number_of_nights to match schema."""
        return self.number_of_nights




    @property
    def is_tour_ended(self) -> bool:
        """Check if the tour has ended."""
        if not self.return_date:
            return False
        return self.return_date < date.today()

    @property
    def created_by_name(self) -> str:
        """Get name of the user who created this itinerary."""
        return self.creator.full_name if self.creator else "Unknown"

    @property
    def base_tour_title(self) -> str | None:
        """Get the title of the original base tour if applicable."""
        return self.created_from_base_tour.tour_name if self.created_from_base_tour else None

    def to_dict(self) -> dict:
        """Convert itinerary to dictionary."""
        return {
            "id": str(self.id),
            "unique_code": self.unique_code,
            "tour_title": self.tour_title,
            "tour_code": self.tour_code,
            "tour_type": self.tour_type.name if self.tour_type else None,
            "number_of_days": self.number_of_days,
            "number_of_nights": self.number_of_nights,
            "hero_image_url": self.hero_image_url,
            "departure_date": self.departure_date.isoformat(),
            "return_date": self.return_date.isoformat(),
            "status": self.status.value,
            "payment_status": self.payment_status.value if self.payment_status else None,
            "is_complete": self.is_complete,
            "creation_method": self.creation_method.value,
            "created_by": self.creator.full_name if self.creator else None,
            "assigned_to": self.assigned_agent.full_name if self.assigned_agent else None,
            "primary_traveler": self.primary_traveler.to_dict() if self.primary_traveler else None,
            "days": [day.to_dict() for day in self.days],
            "inclusions": [inc.to_dict() for inc in self.inclusions],
            "exclusions": [exc.to_dict() for exc in self.exclusions],
            "public_url": self.get_public_url(),
            "is_editable": self.is_editable("cs_agent"),  # Default check
            "is_tour_ended": self.is_tour_ended,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ItineraryDay(Base):
    """
    Itinerary Day model representing individual days in a customer itinerary.
    """
    __tablename__ = "itinerary_days"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Day Information
    day_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Day number in the itinerary"
    )

    day_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Title for the day e.g., 'Arrival in Serengeti'"
    )

    day_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Actual date of this day (auto-calculated from departure_date)"
    )

    # Content (can be auto-filled from DestinationCombination or custom)
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Description of the day"
    )

    activities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Activities for the day"
    )

    meals_included: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Meals included e.g. 'Breakfast, Dinner'"
    )

    # Track if content is custom or auto-filled
    is_description_custom: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="True if description was manually entered, False if auto-filled"
    )

    is_activity_custom: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="True if activities were manually entered, False if auto-filled"
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
    itinerary: Mapped["Itinerary"] = relationship(
        "Itinerary",
        back_populates="days"
    )

    accommodation: Mapped["Accommodation"] = relationship(
        "Accommodation",
        lazy="joined"
    )

    destinations: Mapped[List["Destination"]] = relationship(
        "Destination",
        secondary="itinerary_day_destinations",
        lazy="selectin"
    )

    # Indexes and Constraints
    __table_args__ = (
        CheckConstraint("day_number > 0", name="check_positive_day_number"),
        Index("ix_itinerary_days_itinerary", "itinerary_id", "day_number"),
        Index("ix_itinerary_days_date", "day_date"),
    )

    def __repr__(self) -> str:
        return f"<ItineraryDay {self.day_number}: {self.day_title}>"

    def to_dict(self) -> dict:
        """Convert itinerary day to dictionary."""
        return {
            "id": str(self.id),
            "day_number": self.day_number,
            "day_title": self.day_title,
            "day_date": self.day_date.isoformat(),
            "description": self.description,
            "activities": self.activities,
            "is_description_custom": self.is_description_custom,
            "is_activity_custom": self.is_activity_custom,
            "accommodation": self.accommodation.name if self.accommodation else None,
            "accommodation_id": str(self.accommodation_id) if self.accommodation_id else None,
            "atmospheric_image_url": self.atmospheric_image_url,
            "destinations": [dest.name for dest in self.destinations],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Traveler(Base):
    """
    Traveler model representing travelers in an itinerary.

    Each itinerary can have multiple travelers, with one marked as primary.
    """
    __tablename__ = "travelers"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Primary Contact
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="One traveler should be marked as primary contact"
    )

    # Personal Information
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Email (required for primary traveler)"
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Phone (required for primary traveler)"
    )

    age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Age of traveler"
    )

    nationality: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # Special Requests
    special_requests: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Dietary restrictions, accessibility needs, etc."
    )

    # Internal Notes
    profile_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="CS agent notes about this traveler (not visible to customer)"
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
    itinerary: Mapped["Itinerary"] = relationship(
        "Itinerary",
        back_populates="travelers"
    )

    # Indexes
    __table_args__ = (
        Index("ix_travelers_itinerary", "itinerary_id"),
        Index("ix_travelers_primary", "is_primary"),
    )

    def __repr__(self) -> str:
        primary_tag = " (Primary)" if self.is_primary else ""
        return f"<Traveler {self.full_name}{primary_tag}>"

    def to_dict(self) -> dict:
        """Convert traveler to dictionary."""
        return {
            "id": str(self.id),
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "age": self.age,
            "nationality": self.nationality,
            "is_primary": self.is_primary,
            "special_requests": self.special_requests,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ItineraryImage(Base):
    """
    Itinerary Image model for storing uploaded images custom to an itinerary.
    """
    __tablename__ = "itinerary_images"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Image Information
    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Image URL"
    )
    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    image_role: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Role of the image: cover, accommodation_end, inclusions, about_banner, end"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    itinerary: Mapped["Itinerary"] = relationship(
        "Itinerary",
        back_populates="images"
    )

    # Indexes
    __table_args__ = (
        Index("ix_itinerary_images_sort", "itinerary_id", "sort_order"),
    )

    def __repr__(self) -> str:
        return f"<ItineraryImage for {self.itinerary_id}>"

    def to_dict(self) -> dict:
        """Convert image to dictionary."""
        return {
            "id": str(self.id),
            "itinerary_id": str(self.itinerary_id),
            "image_url": self.image_url,
            "caption": self.caption,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
        }
