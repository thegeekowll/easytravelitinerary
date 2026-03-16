"""
Itinerary-related Pydantic schemas.

This is the most complex schema file - handles itineraries, days, travelers,
and supports 3 different creation methods (choose_existing, edit_existing, custom).
"""
from typing import Annotated, Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from app.models.itinerary import (
    ItineraryStatusEnum,
    CreationMethodEnum,
    PaymentStatusEnum,
    DeliveryStatusEnum
)

from app.schemas.base_tour import TourTypeResponse
from app.schemas.accommodation import AccommodationLevelResponse

if TYPE_CHECKING:
    from app.schemas.destination import DestinationResponse
    from app.schemas.accommodation import AccommodationResponse
    # from app.schemas.user import UserResponse  # If needed


# ========================================
# TRAVELER SCHEMAS
# ========================================

class TravelerBase(BaseModel):
    """Base traveler schema."""

    full_name: Annotated[str, Field(min_length=1, max_length=255, description="Traveler's full name")]
    email: Optional[EmailStr] = None
    phone: Annotated[Optional[str], Field(max_length=50)] = None
    age: Optional[int] = Field(None, description="Age of traveler")
    nationality: Annotated[Optional[str], Field(max_length=100)] = None
    special_requests: Optional[str] = Field(None, description="Dietary restrictions, accessibility needs, etc.")
    is_primary: bool = False

    model_config = ConfigDict(from_attributes=True)


class TravelerCreate(TravelerBase):
    """Schema for creating a traveler."""

    itinerary_id: UUID


class TravelerUpdate(BaseModel):
    """Schema for updating a traveler."""

    full_name: Annotated[Optional[str], Field(min_length=1, max_length=255)] = None
    email: Optional[EmailStr] = None
    phone: Annotated[Optional[str], Field(max_length=50)] = None
    age: Optional[int] = None
    nationality: Annotated[Optional[str], Field(max_length=100)] = None
    special_requests: Optional[str] = None
    is_primary: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class TravelerResponse(TravelerBase):
    """Traveler schema for API responses."""

    id: UUID
    itinerary_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========================================
# ITINERARY IMAGE SCHEMAS
# ========================================

class ItineraryImageBase(BaseModel):
    """Base itinerary image schema."""
    image_url: str
    caption: Optional[str] = None
    sort_order: int = 0
    image_role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ItineraryImageCreate(ItineraryImageBase):
    """Schema for creating an itinerary image."""
    itinerary_id: UUID


class ItineraryImageUpdate(BaseModel):
    """Schema for updating an itinerary image."""
    image_url: Optional[str] = None
    caption: Optional[str] = None
    sort_order: Optional[int] = None
    image_role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ItineraryImageResponse(ItineraryImageBase):
    """Itinerary image schema for API responses."""
    id: UUID
    itinerary_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========================================
# ITINERARY DAY SCHEMAS
# ========================================

class ItineraryDayBase(BaseModel):
    """Base itinerary day schema."""

    day_number: Annotated[int, Field(ge=1, description="Day number in the itinerary")]
    day_title: str
    date: Optional[date] = None
    description: Optional[str] = None
    activities: Optional[str] = None
    accommodation_id: Optional[UUID] = None
    meals_included: Annotated[Optional[str], Field(max_length=100)] = None
    is_description_custom: bool = False
    is_activity_custom: bool = False
    atmospheric_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ItineraryDayCreate(ItineraryDayBase):
    """Schema for creating an itinerary day."""

    itinerary_id: UUID
    destination_ids: List[UUID] = Field(default_factory=list)


class ItineraryDayUpdate(BaseModel):
    """Schema for updating an itinerary day."""

    id: Optional[UUID] = None
    day_number: Annotated[Optional[int], Field(ge=1)] = None
    day_title: Optional[str] = None
    date: Optional[date] = None
    description: Optional[str] = None
    activities: Optional[str] = None
    accommodation_id: Optional[UUID] = None
    meals_included: Annotated[Optional[str], Field(max_length=100)] = None
    is_description_custom: Optional[bool] = None
    is_activity_custom: Optional[bool] = None
    destination_ids: Optional[List[UUID]] = None
    atmospheric_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ItineraryDayResponse(ItineraryDayBase):
    """Itinerary day schema for API responses."""

    id: UUID
    itinerary_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ItineraryDayWithDetails(ItineraryDayResponse):
    """Itinerary day with nested destination and accommodation details."""

    destinations: List['DestinationResponse'] = Field(default_factory=list)
    accommodation: Optional['AccommodationResponse'] = None

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, use_enum_values=True)


# ========================================
# ITINERARY SCHEMAS
# ========================================

class ItineraryBase(BaseModel):
    """Base itinerary schema with common fields."""

    tour_title: Annotated[str, Field(min_length=1, max_length=200, description="Title of the tour/itinerary")]
    client_name: Annotated[str, Field(min_length=1, max_length=255, description="Primary client/customer name")]
    client_email: EmailStr
    client_phone: Annotated[Optional[str], Field(max_length=50)] = None
    number_of_travelers: Annotated[int, Field(ge=0)] = 1
    departure_date: date
    return_date: date
    duration_days: Annotated[Optional[int], Field(ge=1)] = None
    duration_nights: Annotated[Optional[int], Field(ge=0)] = None
    total_price: Annotated[Optional[Decimal], Field(ge=0, max_digits=10, decimal_places=2)] = None
    deposit_amount: Annotated[Optional[Decimal], Field(ge=0, max_digits=10, decimal_places=2)] = None
    currency: Annotated[str, Field(min_length=3, max_length=3)] = "USD"
    payment_status: PaymentStatusEnum = PaymentStatusEnum.NOT_PAID
    status: ItineraryStatusEnum = ItineraryStatusEnum.DRAFT
    notes: Optional[str] = None
    
    # New Fields
    tour_type_id: Optional[UUID] = None
    accommodation_level_id: Optional[UUID] = None
    difficulty_level: Optional[str] = None
    description: Optional[str] = None
    highlights: Optional[str] = None

    @field_validator('currency')
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        """Validate currency code is uppercase and 3 characters."""
        v = v.upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError('Currency code must be exactly 3 letters')
        return v

    @field_validator('return_date')
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Validate return date is after departure date."""
        if 'departure_date' in info.data and v < info.data['departure_date']:
            raise ValueError('return_date must be after departure_date')
        return v

    model_config = ConfigDict(from_attributes=True)


class ItineraryCreateChooseExisting(ItineraryBase):
    """Schema for creating itinerary using CHOOSE_EXISTING method.

    Creates itinerary from a base tour template without modifications.
    """

    creation_method: CreationMethodEnum = CreationMethodEnum.CHOOSE_EXISTING
    base_tour_id: UUID
    assigned_agent_id: Optional[UUID] = None
    travelers: List[TravelerBase] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ItineraryCreateEditExisting(ItineraryBase):
    """Schema for creating itinerary using EDIT_EXISTING method.

    Creates itinerary from a base tour template with custom modifications.
    """

    creation_method: CreationMethodEnum = CreationMethodEnum.EDIT_EXISTING
    base_tour_id: UUID
    assigned_agent_id: Optional[UUID] = None
    days: Optional[List[ItineraryDayCreate]] = None
    inclusion_ids: Optional[List[UUID]] = None
    exclusion_ids: Optional[List[UUID]] = None
    travelers: List[TravelerBase] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ItineraryCreateCustom(ItineraryBase):
    """Schema for creating itinerary using CUSTOM method.

    Creates a fully custom itinerary from scratch.
    """

    creation_method: CreationMethodEnum = CreationMethodEnum.CUSTOM
    assigned_agent_id: Optional[UUID] = None
    tour_type_id: UUID
    accommodation_level_id: Optional[UUID] = None
    days: Annotated[List[ItineraryDayCreate], Field(min_length=1)]
    inclusion_ids: List[UUID] = Field(default_factory=list)
    exclusion_ids: List[UUID] = Field(default_factory=list)
    description: Optional[str] = None
    featured_accommodation_ids: List[UUID] = Field(default_factory=list)
    travelers: List[TravelerBase] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ItineraryUpdate(BaseModel):
    """Schema for updating an existing itinerary.

    All fields are optional to support partial updates.
    """

    tour_title: Annotated[Optional[str], Field(min_length=1, max_length=200)] = None
    client_name: Annotated[Optional[str], Field(min_length=1, max_length=255)] = None
    client_email: Optional[EmailStr] = None
    client_phone: Annotated[Optional[str], Field(max_length=50)] = None
    number_of_travelers: Annotated[Optional[int], Field(ge=1)] = None
    departure_date: Optional[date] = None
    return_date: Optional[date] = None
    total_price: Annotated[Optional[Decimal], Field(ge=0, max_digits=10, decimal_places=2)] = None
    deposit_amount: Annotated[Optional[Decimal], Field(ge=0, max_digits=10, decimal_places=2)] = None
    currency: Annotated[Optional[str], Field(min_length=3, max_length=3)] = None
    payment_status: Optional[PaymentStatusEnum] = None
    status: Optional[ItineraryStatusEnum] = None
    notes: Optional[str] = None
    assigned_agent_id: Optional[UUID] = None
    inclusion_ids: Optional[List[UUID]] = None
    exclusion_ids: Optional[List[UUID]] = None
    
    # New Fields
    tour_type_id: Optional[UUID] = None
    accommodation_level_id: Optional[UUID] = None
    difficulty_level: Optional[str] = None
    description: Optional[str] = None
    highlights: Optional[str] = None
    
    days: Optional[List[ItineraryDayUpdate]] = None
    inclusion_ids: Optional[List[UUID]] = None
    exclusion_ids: Optional[List[UUID]] = None

    @field_validator('currency')
    @classmethod
    def validate_currency_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate currency code is uppercase and 3 characters."""
        if v is None:
            return v
        v = v.upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError('Currency code must be exactly 3 letters')
        return v

    model_config = ConfigDict(from_attributes=True)


class ItineraryResponse(ItineraryBase):
    """Itinerary schema for API responses without nested data."""

    id: UUID
    unique_code: str
    creation_method: CreationMethodEnum
    base_tour_id: Optional[UUID] = None
    base_tour_title: Optional[str] = None
    created_by_user_id: UUID
    created_by_name: Optional[str] = None
    assigned_agent_id: Optional[UUID] = None
    last_sent_at: Optional[datetime] = None
    delivery_status: Optional[DeliveryStatusEnum] = None
    payment_status: Optional[PaymentStatusEnum] = None
    created_at: datetime
    updated_at: datetime
    images: List[ItineraryImageResponse] = Field(default_factory=list)
    
    # Nested Relationships (for easy display)
    tour_type: Optional['TourTypeResponse'] = None
    accommodation_level: Optional['AccommodationLevelResponse'] = None

    model_config = ConfigDict(from_attributes=True)


class ItineraryWithDetails(ItineraryResponse):
    """Itinerary schema with all nested related data.

    This is the comprehensive response including days, travelers, inclusions, etc.
    Used for detailed itinerary views and PDF generation.
    """

    days: List[ItineraryDayWithDetails] = Field(default_factory=list)
    travelers: List[TravelerResponse] = Field(default_factory=list)
    inclusions: List['InclusionResponse'] = Field(default_factory=list)
    exclusions: List['ExclusionResponse'] = Field(default_factory=list)
    featured_accommodations: List['AccommodationResponse'] = Field(default_factory=list)
    created_by: Optional['UserResponse'] = None
    assigned_agent: Optional['UserResponse'] = None
    assigned_agent: Optional['UserResponse'] = None
    base_tour: Optional['BaseTourResponse'] = None
    images: List[ItineraryImageResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ItineraryPublicView(BaseModel):
    """Public-facing itinerary schema for client view.

    Excludes internal fields like notes, pricing details, etc.
    Accessed via unique_code URL.
    """

    unique_code: str
    tour_title: str
    client_name: str
    departure_date: date
    return_date: date
    duration_days: Optional[int]
    duration_nights: Optional[int] = None
    tour_type: Optional[str] = None
    accommodation_level: Optional[str] = None
    hero_image_url: Optional[str] = None
    welcome_message: Optional[str] = None
    status: ItineraryStatusEnum
    days: List[ItineraryDayWithDetails]
    travelers: List[TravelerResponse]
    inclusions: List['InclusionResponse']
    exclusions: List['ExclusionResponse']
    featured_accommodations: List['AccommodationResponse']
    images: List[ItineraryImageResponse]
    company_about: Optional[str] = None
    company_badges: List['CompanyAssetResponse'] = Field(default_factory=list)
    agent_name: Optional[str] = None
    agent_email: Optional[str] = None
    agent_position: Optional[str] = None
    footer_notes: Optional[str] = None # Added footer_notes
    agent_phone: Optional[str] = None
    agent_profile_photo_url: Optional[str] = None
    
    # Company Details
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    company_website: Optional[str] = None
    company_socials: Dict[str, str] = Field(default_factory=dict)
    
    closing_message: Optional[str] = None
    logo_url: Optional[str] = None
    review_image_url: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('tour_type', mode='before')
    @classmethod
    def get_tour_type_name(cls, v):
        if hasattr(v, 'name'):
            return v.name
        return v

    @field_validator('accommodation_level', mode='before')
    @classmethod
    def get_accommodation_level_name(cls, v):
        if hasattr(v, 'name'):
            return v.name
        return v


class ItineraryStatusChange(BaseModel):
    """Schema for changing itinerary status."""

    new_status: ItineraryStatusEnum
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Rebuild models to resolve forward references
# This must be called after all models are defined
def _rebuild_models():
    """Rebuild Pydantic models to resolve forward references."""
    try:
        # Import the actual schemas
        from app.schemas.destination import DestinationResponse  # noqa: F401
        from app.schemas.accommodation import AccommodationResponse  # noqa: F401
        from app.schemas.inclusion import InclusionResponse  # noqa: F401
        from app.schemas.exclusion import ExclusionResponse  # noqa: F401
        from app.schemas.user import UserResponse  # noqa: F401
        from app.schemas.base_tour import BaseTourResponse  # noqa: F401
        from app.schemas.company import CompanyAssetResponse  # noqa: F401

        # Rebuild models that use forward references
        ItineraryDayWithDetails.model_rebuild()
        ItineraryWithDetails.model_rebuild()
        ItineraryPublicView.model_rebuild()
    except ImportError:
        # Schemas not yet available, will be rebuilt later
        pass


class ItineraryAssignRequest(BaseModel):
    """Schema for assigning itinerary to an agent."""

    assigned_to_user_id: UUID

    model_config = ConfigDict(from_attributes=True)


# Call rebuild at the end of file to fix forward references
_rebuild_models()

