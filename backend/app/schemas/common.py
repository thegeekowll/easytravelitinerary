"""
Common Pydantic schemas used across the application.

This module contains generic response schemas for pagination, messages, and errors.
"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

# Generic type variable for pagination
T = TypeVar('T')


class MessageResponse(BaseModel):
    """Standard success message response."""

    message: str = Field(
        ...,
        description="Success or informational message"
    )

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(
        ...,
        description="Error message describing what went wrong"
    )
    error_code: Optional[str] = Field(
        None,
        description="Optional error code for client-side error handling"
    )

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Used for list endpoints that support pagination.
    """

    items: List[T] = Field(
        ...,
        description="List of items for the current page"
    )
    total: int = Field(
        ...,
        description="Total number of items across all pages",
        ge=0
    )
    page: int = Field(
        ...,
        description="Current page number (1-indexed)",
        ge=1
    )
    page_size: int = Field(
        ...,
        description="Number of items per page",
        ge=1,
        le=100
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages",
        ge=0
    )
    has_next: bool = Field(
        ...,
        description="Whether there is a next page available"
    )
    has_prev: bool = Field(
        ...,
        description="Whether there is a previous page available"
    )

    model_config = ConfigDict(from_attributes=True)
