"""
Exclusion-related Pydantic schemas.

This module contains schemas for managing tour/itinerary exclusions.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ExclusionBase(BaseModel):
    """Base exclusion schema with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the exclusion (e.g., 'International flights')"
    )
    icon_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Icon name for UI display"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Detailed description"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL to an illustrative image"
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Category for grouping exclusions"
    )
    sort_order: int = Field(
        default=0,
        description="Order for displaying exclusions"
    )

    model_config = ConfigDict(from_attributes=True)


class ExclusionCreate(ExclusionBase):
    """Schema for creating a new exclusion."""

    pass


class ExclusionUpdate(BaseModel):
    """Schema for updating an existing exclusion.

    All fields are optional to support partial updates.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated exclusion name"
    )
    icon_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated icon name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Detailed description"
    )
    image_url: Optional[str] = Field(
        None,
        description="Updated image URL"
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated category"
    )
    sort_order: Optional[int] = Field(
        None,
        description="Updated sort order"
    )

    model_config = ConfigDict(from_attributes=True)


class ExclusionResponse(ExclusionBase):
    """Exclusion schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique exclusion identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the exclusion was created"
    )

    model_config = ConfigDict(from_attributes=True)
