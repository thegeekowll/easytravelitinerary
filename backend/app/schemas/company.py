"""
Company-related Pydantic schemas.

This module contains schemas for managing company content and assets.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, HttpUrl


class CompanyContentBase(BaseModel):
    """Base company content schema.

    Used for managing company information displayed in itineraries and communications.
    """
    key: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique key identifying this content (e.g., 'company_name', 'footer_text')"
    )
    content: str = Field(
        ...,
        description="The actual content/text"
    )
    placeholders: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Available placeholders for template"
    )

    model_config = ConfigDict(from_attributes=True)


class CompanyAssetLink(BaseModel):
    """Schema for linking an existing asset (from URL)."""
    asset_url: str
    asset_type: str
    asset_name: Optional[str] = None
    title: Optional[str] = None



class CompanyContentCreate(CompanyContentBase):
    """Schema for creating new company content."""

    pass


class CompanyContentUpdate(BaseModel):
    """Schema for updating company content.

    All fields are optional to support partial updates.
    """

    key: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated content key"
    )
    content: Optional[str] = Field(
        None,
        description="Updated content value"
    )
    placeholders: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated placeholders"
    )

    model_config = ConfigDict(from_attributes=True)


class CompanyContentResponse(CompanyContentBase):
    """Company content schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique content identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the content was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the content was last updated"
    )

    model_config = ConfigDict(from_attributes=True)


class CompanyAssetBase(BaseModel):
    """Base company asset schema.

    Used for managing company logos, images, and other digital assets.
    """

    asset_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique key/name identifying this asset"
    )
    asset_url: str = Field(
        ...,
        description="URL where the asset is stored"
    )
    asset_type: str = Field(
        ...,
        max_length=50,
        description="Type of asset (image, pdf, video, etc.)"
    )
    sort_order: int = Field(
        default=0,
        description="Display order"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this asset is currently active/in-use"
    )

    model_config = ConfigDict(from_attributes=True)


class CompanyAssetCreate(CompanyAssetBase):
    """Schema for creating a new company asset."""

    pass


class CompanyAssetUpdate(BaseModel):
    """Schema for updating a company asset.

    All fields are optional to support partial updates.
    """

    asset_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated asset name"
    )
    asset_url: Optional[str] = Field(
        None,
        description="Updated asset URL"
    )
    asset_type: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated asset type"
    )
    sort_order: Optional[int] = Field(
        None,
        description="Updated sort order"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Updated active status"
    )

    model_config = ConfigDict(from_attributes=True)


class CompanyAssetResponse(CompanyAssetBase):
    """Company asset schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique asset identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the asset was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the asset was last updated"
    )

    model_config = ConfigDict(from_attributes=True)
