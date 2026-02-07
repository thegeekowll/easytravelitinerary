"""
Accommodation-related Pydantic schemas.

This module contains schemas for managing accommodations, their types, and images.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, HttpUrl, field_validator


class AccommodationTypeBase(BaseModel):
    """Base accommodation type schema."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Accommodation type name (e.g., 'Hotel', 'Resort', 'Boutique Hotel')"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Description of this accommodation type"
    )

    model_config = ConfigDict(from_attributes=True)


class AccommodationTypeCreate(AccommodationTypeBase):
    """Schema for creating a new accommodation type."""

    pass


class AccommodationTypeUpdate(BaseModel):
    """Schema for updating an accommodation type."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated type name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated description"
    )

    model_config = ConfigDict(from_attributes=True)


class AccommodationTypeResponse(AccommodationTypeBase):
    """Accommodation type schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique accommodation type identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the accommodation type was created"
    )

    model_config = ConfigDict(from_attributes=True)


class AccommodationLevelBase(BaseModel):
    """Base accommodation level schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)


class AccommodationLevelCreate(AccommodationLevelBase):
    pass


class AccommodationLevelResponse(AccommodationLevelBase):
    id: UUID
    created_at: datetime



class AccommodationImageBase(BaseModel):
    """Base accommodation image schema."""

    image_url: HttpUrl = Field(
        ...,
        description="URL to the accommodation image"
    )
    caption: Optional[str] = Field(
        None,
        max_length=500,
        description="Image caption or description"
    )
    is_primary: bool = Field(
        default=False,
        description="Whether this is the primary/featured image"
    )
    display_order: int = Field(
        default=0,
        description="Order in which to display this image",
        ge=0
    )

    model_config = ConfigDict(from_attributes=True)


class AccommodationImageCreate(AccommodationImageBase):
    """Schema for creating a new accommodation image."""

    accommodation_id: UUID = Field(
        ...,
        description="ID of the accommodation this image belongs to"
    )


class AccommodationImageUpdate(BaseModel):
    """Schema for updating an accommodation image."""

    image_url: Optional[HttpUrl] = Field(
        None,
        description="Updated image URL"
    )
    caption: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated caption"
    )
    is_primary: Optional[bool] = Field(
        None,
        description="Updated primary status"
    )
    display_order: Optional[int] = Field(
        None,
        ge=0,
        description="Updated display order"
    )

    model_config = ConfigDict(from_attributes=True)


class AccommodationImageResponse(AccommodationImageBase):
    """Accommodation image schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique image identifier"
    )
    accommodation_id: UUID = Field(
        ...,
        description="ID of the accommodation this image belongs to"
    )
    created_at: datetime = Field(
        ...,
        description="When the image was added"
    )

    model_config = ConfigDict(from_attributes=True)


class AccommodationBase(BaseModel):
    """Base accommodation schema with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Accommodation name"
    )
    type_id: UUID = Field(
        ...,
        description="ID of the accommodation type (hotel, resort, etc.)"
    )
    level_id: Optional[UUID] = Field(
        None,
        description="ID of the accommodation level (Basic, Luxury, etc.)"
    )
    location_destination_id: UUID = Field(
        ...,
        description="ID of the destination where this accommodation is located"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the accommodation"
    )
    address: Optional[str] = Field(
        None,
        max_length=500,
        description="Physical address"
    )
    gps_coordinates: Optional[str] = Field(
        None,
        max_length=100,
        description="GPS coordinates in 'latitude,longitude' format"
    )
    star_rating: Optional[Decimal] = Field(
        None,
        description="Star rating (0.0 to 5.0)",
        ge=0,
        le=5
    )
    price_range: Optional[str] = Field(
        None,
        max_length=50,
        description="Price range indicator (e.g., '$$$', '€100-€200 per night')"
    )
    amenities: Optional[List[str]] = Field(
        default=None,
        description="List of amenities"
    )
    contact_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSONB field containing contact information"
    )
    check_in_time: Optional[str] = Field(
        None,
        max_length=20,
        description="Check-in time"
    )
    check_out_time: Optional[str] = Field(
        None,
        max_length=20,
        description="Check-out time"
    )

    @field_validator('gps_coordinates')
    @classmethod
    def validate_gps_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate GPS coordinates format."""
        if v is None:
            return v

        try:
            parts = v.split(',')
            if len(parts) != 2:
                raise ValueError('GPS coordinates must be in format "latitude,longitude"')

            lat = float(parts[0].strip())
            lon = float(parts[1].strip())

            if not (-90 <= lat <= 90):
                raise ValueError('Latitude must be between -90 and 90')
            if not (-180 <= lon <= 180):
                raise ValueError('Longitude must be between -180 and 180')

        except (ValueError, AttributeError) as e:
            raise ValueError(f'Invalid GPS coordinates format: {str(e)}')

        return v

    model_config = ConfigDict(from_attributes=True)


class AccommodationCreate(AccommodationBase):
    """Schema for creating a new accommodation."""

    pass


class AccommodationUpdate(BaseModel):
    """Schema for updating an existing accommodation.

    All fields are optional to support partial updates.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated accommodation name"
    )
    type_id: Optional[UUID] = Field(
        None,
        description="Updated accommodation type ID"
    )
    level_id: Optional[UUID] = Field(
        None,
        description="Updated accommodation level ID"
    )
    location_destination_id: Optional[UUID] = Field(
        None,
        description="Updated destination ID"
    )
    description: Optional[str] = Field(
        None,
        description="Updated description"
    )
    address: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated address"
    )
    gps_coordinates: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated GPS coordinates"
    )
    star_rating: Optional[Decimal] = Field(
        None,
        ge=0,
        le=5,
        description="Updated star rating"
    )
    price_range: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated price range"
    )
    amenities: Optional[List[str]] = Field(
        None,
        description="Updated amenities"
    )
    contact_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated contact info"
    )
    check_in_time: Optional[str] = Field(
        None,
        max_length=20,
        description="Updated check-in time"
    )
    check_out_time: Optional[str] = Field(
        None,
        max_length=20,
        description="Updated check-out time"
    )

    @field_validator('gps_coordinates')
    @classmethod
    def validate_gps_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate GPS coordinates format."""
        if v is None:
            return v

        try:
            parts = v.split(',')
            if len(parts) != 2:
                raise ValueError('GPS coordinates must be in format "latitude,longitude"')

            lat = float(parts[0].strip())
            lon = float(parts[1].strip())

            if not (-90 <= lat <= 90):
                raise ValueError('Latitude must be between -90 and 90')
            if not (-180 <= lon <= 180):
                raise ValueError('Longitude must be between -180 and 180')

        except (ValueError, AttributeError) as e:
            raise ValueError(f'Invalid GPS coordinates format: {str(e)}')

        return v

    model_config = ConfigDict(from_attributes=True)


class AccommodationResponse(AccommodationBase):
    """Accommodation schema for API responses."""

    id: UUID = Field(..., description="Unique accommodation identifier")
    created_at: datetime = Field(..., description="When the accommodation was created")
    updated_at: datetime = Field(..., description="When the accommodation was last updated")
    
    # Include nested details by default for simplicity in list views
    accommodation_type: Optional[AccommodationTypeResponse] = Field(None, description="Accommodation type details")
    accommodation_level: Optional[AccommodationLevelResponse] = Field(None, description="Accommodation level details")
    images: List[AccommodationImageResponse] = Field(default_factory=list, description="List of accommodation images")

    model_config = ConfigDict(from_attributes=True)


class AccommodationWithDetails(AccommodationResponse):
    """Deprecated: Merged into AccommodationResponse, kept for backward compatibility if needed."""
    pass
