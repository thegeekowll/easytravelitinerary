"""
Permission-related Pydantic schemas.

This module contains schemas for managing granular user permissions.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class PermissionBase(BaseModel):
    """Base permission schema with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Permission name (e.g., 'create_itinerary', 'view_reports')"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Human-readable description of what this permission allows"
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="Permission category for grouping (e.g., 'itinerary', 'user_management')"
    )

    model_config = ConfigDict(from_attributes=True)


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission.

    Used by admins to define new permissions in the system.
    """

    pass


class PermissionUpdate(BaseModel):
    """Schema for updating an existing permission.

    All fields are optional to support partial updates.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated permission name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated description"
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated category"
    )

    model_config = ConfigDict(from_attributes=True)


class PermissionResponse(PermissionBase):
    """Permission schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique permission identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the permission was created"
    )

    model_config = ConfigDict(from_attributes=True)


class PermissionAssignment(BaseModel):
    """Schema for assigning permissions to users."""

    user_id: UUID = Field(
        ...,
        description="ID of the user to assign permissions to"
    )
    permission_ids: list[UUID] = Field(
        ...,
        description="List of permission IDs to assign"
    )

    model_config = ConfigDict(from_attributes=True)
