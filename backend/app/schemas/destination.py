"""
Destination-related Pydantic schemas.

This module contains schemas for managing destinations and their images.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, HttpUrl, field_validator


class DestinationImageBase(BaseModel):
    """Base destination image schema."""

    image_url: HttpUrl = Field(
        ...,
        description="URL to the destination image"
    )
    caption: Optional[str] = Field(
        None,
        max_length=500,
        description="Image caption or description"
    )
    is_primary: bool = Field(
        default=False,
        description="Whether this is the primary/featured image for the destination"
    )
    display_order: int = Field(
        default=0,
        description="Order in which to display this image (lower numbers first)",
        ge=0
    )

    model_config = ConfigDict(from_attributes=True)


class DestinationImageCreate(DestinationImageBase):
    """Schema for creating a new destination image."""

    destination_id: UUID = Field(
        ...,
        description="ID of the destination this image belongs to"
    )


class DestinationImageUpdate(BaseModel):
    """Schema for updating a destination image."""

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


class DestinationImageResponse(DestinationImageBase):
    """Destination image schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique image identifier"
    )
    destination_id: UUID = Field(
        ...,
        description="ID of the destination this image belongs to"
    )
    created_at: datetime = Field(
        ...,
        description="When the image was added"
    )

    model_config = ConfigDict(from_attributes=True)


class DestinationBase(BaseModel):
    """Base destination schema with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Destination name"
    )
    country: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Country name"
    )
    region: Optional[str] = Field(
        None,
        max_length=100,
        description="Region or state within the country"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed destination description"
    )
    gps_coordinates: Optional[str] = Field(
        None,
        max_length=100,
        description="GPS coordinates in 'latitude,longitude' format"
    )
    timezone: Optional[str] = Field(
        None,
        max_length=50,
        description="IANA timezone identifier"
    )
    best_time_to_visit: Optional[str] = Field(
        None,
        max_length=200,
        description="Recommended time of year to visit"
    )
    attractions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSONB field containing list of attractions and points of interest"
    )
    travel_tips: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSONB field containing travel tips and recommendations"
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


class DestinationCreate(DestinationBase):
    """Schema for creating a new destination."""

    image_urls: Optional[List[str]] = Field(
        None,
        description="List of image URLs to add immediately"
    )


class DestinationUpdate(BaseModel):
    """Schema for updating an existing destination.

    All fields are optional to support partial updates.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated destination name"
    )
    country: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated country name"
    )
    region: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated region"
    )
    description: Optional[str] = Field(
        None,
        description="Updated description"
    )
    gps_coordinates: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated GPS coordinates"
    )
    timezone: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated timezone"
    )
    best_time_to_visit: Optional[str] = Field(
        None,
        max_length=200,
        description="Updated best time to visit"
    )
    attractions: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated attractions data"
    )
    travel_tips: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated travel tips"
    )
    image_urls: Optional[List[str]] = Field(
        None,
        description="List of image URLs to replace existing images with"
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


class DestinationResponse(DestinationBase):
    """Destination schema for API responses without nested images."""

    id: UUID = Field(
        ...,
        description="Unique destination identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the destination was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the destination was last updated"
    )

    model_config = ConfigDict(from_attributes=True)


class DestinationWithImages(DestinationResponse):
    """Destination schema with nested image data.

    Used when full destination details including images are needed.
    """

    images: List[DestinationImageResponse] = Field(
        default_factory=list,
        description="List of images for this destination"
    )

    model_config = ConfigDict(from_attributes=True)
