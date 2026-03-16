"""
DestinationCombination-related Pydantic schemas.

This module contains schemas for the 2D destination combination table used for auto-filling
descriptions and activities when multiple destinations are selected.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class DestinationCombinationBase(BaseModel):
    """Base destination combination schema.

    This 2D table stores pre-written content for specific combinations of destinations.
    When an agent creates an itinerary day with multiple destinations, the system
    looks up the combination in this table to auto-fill descriptions and activities.
    """

    destination_1_id: UUID = Field(
        ...,
        description="ID of the first destination in the combination"
    )
    destination_2_id: Optional[UUID] = Field(
        None,
        description="ID of the second destination in the combination (optional for diagonal)"
    )
    description_content: str = Field(
        ...,
        description="Pre-written description for when both destinations are visited together"
    )
    activity_content: Optional[str] = Field(
        None,
        description="Suggested activities when visiting both destinations"
    )
    travel_time_minutes: Optional[int] = Field(
        None,
        description="Estimated travel time between the two destinations in minutes",
        ge=0
    )
    transportation_mode: Optional[str] = Field(
        None,
        max_length=100,
        description="Recommended transportation between destinations"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes or tips for this destination combination"
    )

    model_config = ConfigDict(from_attributes=True)


class DestinationCombinationCreate(DestinationCombinationBase):
    """Schema for creating a new destination combination.

    This is used to populate the 2D lookup table with pre-written content
    for common destination pairs.
    """

    bidirectional: bool = Field(
        False,
        description="If true, creates the reverse combination (B->A) as well"
    )


class DestinationCombinationUpdate(BaseModel):
    """Schema for updating an existing destination combination.

    All fields are optional to support partial updates.
    Note: destination IDs typically shouldn't change; create a new record instead.
    """

    description_content: Optional[str] = Field(
        None,
        description="Updated combined description"
    )
    activity_content: Optional[str] = Field(
        None,
        description="Updated activities"
    )
    travel_time_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Updated travel time"
    )
    transportation_mode: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated transportation mode"
    )
    notes: Optional[str] = Field(
        None,
        description="Updated notes"
    )
    bidirectional: Optional[bool] = Field(
        False,
        description="If true, updates the reverse combination (B->A) as well"
    )

    model_config = ConfigDict(from_attributes=True)


class DestinationCombinationResponse(DestinationCombinationBase):
    """Destination combination schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique combination identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the combination was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the combination was last updated"
    )

    model_config = ConfigDict(from_attributes=True)


class DestinationCombinationWithDestinations(DestinationCombinationResponse):
    """Destination combination with full destination details.

    Includes the actual destination objects, not just IDs.
    """

    destination_1: 'DestinationResponse' = Field(
        ...,
        description="First destination in the combination"
    )
    destination_2: Optional['DestinationResponse'] = Field(
        None,
        description="Second destination in the combination"
    )

    model_config = ConfigDict(from_attributes=True)


class DestinationCombinationLookup(BaseModel):
    """Schema for looking up destination combinations.

    Used to query the 2D table for auto-fill data.
    """

    destination_ids: list[UUID] = Field(
        ...,
        min_length=1,
        description="List of destination IDs in sequential order"
    )
    mode: str = Field(
        "chain",
        description="Auto-fill mode: 'chain' (sequential A->B->C) or 'suggest' (combinatorial A-B, A-C...)"
    )

    model_config = ConfigDict(from_attributes=True)


class AutoFillResponse(BaseModel):
    """Response for auto-fill destination combination requests."""

    type: str = Field(..., description="Type of response: 'single', 'pair', or 'multiple'")
    description: Optional[str] = Field(None, description="Combined description if available")
    activity: Optional[str] = Field(None, description="Combined activities if available")
    suggestions: list[DestinationCombinationResponse] = Field(
        default_factory=list,
        description="List of combination suggestions for multiple destinations"
    )

    model_config = ConfigDict(from_attributes=True)


class DestinationGridItem(BaseModel):
    """Destination summary for grid view."""
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class GridCellData(BaseModel):
    """Cell data for the 2D grid matrix."""
    combination_id: Optional[UUID] = None
    has_content: bool = False
    description_preview: Optional[str] = None
    activity_preview: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CombinationGridResponse(BaseModel):
    """Response for the 2D combination grid view."""
    row_destinations: list[DestinationGridItem] = Field(
        default_factory=list,
        description="Destinations for row headers"
    )
    col_destinations: list[DestinationGridItem] = Field(
        default_factory=list,
        description="Destinations for column headers"
    )
    cells: dict[str, GridCellData] = Field(
        default_factory=dict,
        description="Cell data keyed by 'row_id:col_id'"
    )
    combinations: list[DestinationCombinationResponse] = Field(
        default_factory=list,
        description="List of raw combination objects"
    )
    total_destinations: int = Field(0, description="Total number of destinations")
    page_row: int = Field(0, description="Current row page")
    page_col: int = Field(0, description="Current column page")
    page_size: int = Field(20, description="Items per page")

    model_config = ConfigDict(from_attributes=True)


# Import at the end to avoid circular imports
from app.schemas.destination import DestinationResponse
DestinationCombinationWithDestinations.model_rebuild()
