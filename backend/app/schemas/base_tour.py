"""
BaseTour-related Pydantic schemas.

This module contains schemas for managing base tours (templates), tour types, days, and images.
"""
from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, HttpUrl

from .destination import DestinationResponse
from .inclusion import InclusionResponse
from .exclusion import ExclusionResponse
from .accommodation import AccommodationLevelResponse


class TourTypeBase(BaseModel):
    """Base tour type schema."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Tour type name (e.g., 'Cultural', 'Adventure', 'Luxury')"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Description of this tour type"
    )

    model_config = ConfigDict(from_attributes=True)


class TourTypeCreate(TourTypeBase):
    """Schema for creating a new tour type."""

    pass


class TourTypeUpdate(BaseModel):
    """Schema for updating a tour type."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated tour type name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated description"
    )

    model_config = ConfigDict(from_attributes=True)


class TourTypeResponse(TourTypeBase):
    """Tour type schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique tour type identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the tour type was created"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourImageBase(BaseModel):
    """Base tour image schema."""

    image_url: str = Field(
        ...,
        description="URL to the tour image"
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
    image_role: Optional[str] = Field(
        None,
        description="Role of the image (cover, etc.)"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourImageCreate(BaseTourImageBase):
    """Schema for creating a new base tour image."""

    base_tour_id: UUID = Field(
        ...,
        description="ID of the base tour this image belongs to"
    )

class BaseTourImageLink(BaseModel):
    """Schema for linking an existing image by URL."""
    image_url: str
    caption: Optional[str] = None
    image_role: Optional[str] = None



class BaseTourImageUpdate(BaseModel):
    """Schema for updating a base tour image."""

    image_url: Optional[str] = Field(
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
    image_role: Optional[str] = Field(
        None,
        description="Updated image role"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourImageResponse(BaseTourImageBase):
    """Base tour image schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique image identifier"
    )
    base_tour_id: UUID = Field(
        ...,
        description="ID of the base tour this image belongs to"
    )
    created_at: datetime = Field(
        ...,
        description="When the image was added"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourDayBase(BaseModel):
    """Base tour day schema."""

    day_number: int = Field(
        ...,
        description="Day number in the tour sequence",
        ge=1
    )
    day_title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Day title or summary"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of activities for this day"
    )
    activities: Optional[str] = Field(
        None,
        description="Specific activities planned for this day"
    )
    meals_included: Optional[str] = Field(
        None,
        max_length=100,
        description="Meals included (e.g., 'B, L, D')"
    )


    model_config = ConfigDict(from_attributes=True)


class BaseTourDayCreate(BaseTourDayBase):
    """Schema for creating a new base tour day."""

    base_tour_id: Optional[UUID] = Field(
        None,
        description="ID of the base tour this day belongs to"
    )
    destination_ids: List[UUID] = Field(
        default_factory=list,
        description="List of destination IDs visited on this day"
    )
    accommodation_id: Optional[UUID] = Field(
        None,
        description="ID of the accommodation for this day"
    )


class BaseTourDayUpdate(BaseModel):
    """Schema for updating a base tour day."""

    day_number: Optional[int] = Field(
        None,
        ge=1,
        description="Updated day number"
    )
    day_title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated title"
    )
    description: Optional[str] = Field(
        None,
        description="Updated description"
    )
    activities: Optional[str] = Field(
        None,
        description="Updated activities"
    )
    meals_included: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated meals included"
    )

    destination_ids: Optional[List[UUID]] = Field(
        None,
        description="Updated list of destination IDs"
    )

    accommodation_id: Optional[UUID] = Field(
        None,
        description="Updated accommodation ID"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourDayResponse(BaseTourDayBase):
    """Base tour day schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique day identifier"
    )
    base_tour_id: UUID = Field(
        ...,
        description="ID of the base tour this day belongs to"
    )
    created_at: datetime = Field(
        ...,
        description="When the day was created"
    )
    accommodation_id: Optional[UUID] = Field(
        None,
        description="ID of the accommodation"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourDayWithDestinations(BaseTourDayResponse):
    """Base tour day schema with nested destination data."""

    destinations: List[DestinationResponse] = Field(
        default_factory=list,
        description="List of destinations visited on this day"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourBase(BaseModel):
    """Base tour schema with common fields."""

    tour_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Tour title"
    )
    tour_type_id: UUID = Field(
        ...,
        description="ID of the tour type (cultural, adventure, etc.)"
    )
    number_of_days: int = Field(
        ...,
        description="Total duration in days",
        ge=1
    )
    # Added number_of_nights as it is in model and required
    number_of_nights: int = Field(
        ...,
        description="Total duration in nights",
        ge=0
    )
    description: Optional[str] = Field(
        None,
        description="Detailed tour description"
    )
    highlights: Optional[str] = Field(
        None,
        description="Tour highlights and key features"
    )
    difficulty_level: Optional[str] = Field(
        None,
        max_length=50,
        description="Difficulty level (e.g., 'Easy', 'Moderate', 'Challenging')"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this tour is currently active/available"
    )
    tour_code: Optional[str] = Field(
        None,
        description="Unique tour code"
    )
    accommodation_level_id: Optional[UUID] = Field(
        None,
        description="ID of the accommodation level (Luxury, Mid-range, etc.)"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourCreate(BaseTourBase):
    """Schema for creating a new base tour."""
    
    days: List[BaseTourDayCreate] = Field(
        default_factory=list,
        description="List of tour days"
    )
    inclusion_ids: List[UUID] = Field(
        default_factory=list,
        description="List of inclusion IDs"
    )
    exclusion_ids: List[UUID] = Field(
        default_factory=list,
        description="List of exclusion IDs"
    )


class BaseTourUpdate(BaseModel):
    """Schema for updating a base tour.

    All fields are optional to support partial updates.
    """

    tour_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated tour title"
    )
    tour_type_id: Optional[UUID] = Field(
        None,
        description="Updated tour type ID"
    )
    number_of_days: Optional[int] = Field(
        None,
        ge=1,
        description="Updated duration"
    )
    number_of_nights: Optional[int] = Field(
        None,
        ge=0,
        description="Updated nights"
    )
    description: Optional[str] = Field(
        None,
        description="Updated description"
    )
    highlights: Optional[str] = Field(
        None,
        description="Updated highlights"
    )
    difficulty_level: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated difficulty level"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Updated active status"
    )
    tour_code: Optional[str] = Field(
        None,
        description="Updated tour code"
    )
    accommodation_level_id: Optional[UUID] = Field(
        None,
        description="Updated accommodation level ID"
    )
    days: Optional[List[BaseTourDayCreate]] = Field(
        None,
        description="Updated list of days (replaces existing)"
    )
    inclusion_ids: Optional[List[UUID]] = Field(
        None,
        description="Updated list of inclusion IDs"
    )
    exclusion_ids: Optional[List[UUID]] = Field(
        None,
        description="Updated list of exclusion IDs"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourResponse(BaseTourBase):
    """Base tour schema for API responses without nested data."""

    id: UUID = Field(
        ...,
        description="Unique base tour identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the tour was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the tour was last updated"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseTourWithDetails(BaseTourResponse):
    """Base tour schema with all nested related data.

    Includes tour type, days with destinations, images, inclusions, and exclusions.
    """

    tour_type: Optional[TourTypeResponse] = Field(
        None,
        description="Tour type details"
    )
    accommodation_level: Optional[AccommodationLevelResponse] = Field(
        None,
        description="Accommodation level details"
    )
    days: List[BaseTourDayWithDestinations] = Field(
        default_factory=list,
        description="List of tour days with destinations"
    )
    images: List[BaseTourImageResponse] = Field(
        default_factory=list,
        description="List of tour images"
    )
    inclusions: List[InclusionResponse] = Field(
        default_factory=list,
        description="What's included in this tour"
    )
    exclusions: List[ExclusionResponse] = Field(
        default_factory=list,
        description="What's not included in this tour"
    )

    model_config = ConfigDict(from_attributes=True)


# Rebuild models to resolve forward references
BaseTourWithDetails.model_rebuild()
BaseTourDayWithDestinations.model_rebuild()
