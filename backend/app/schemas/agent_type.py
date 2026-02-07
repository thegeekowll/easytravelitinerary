"""
AgentType-related Pydantic schemas.

This module contains schemas for managing travel agent specialization categories.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AgentTypeBase(BaseModel):
    """Base agent type schema with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Agent type name (e.g., 'Europe Specialist', 'Adventure Tours')"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed description of this agent specialization"
    )

    model_config = ConfigDict(from_attributes=True)


class AgentTypeCreate(AgentTypeBase):
    """Schema for creating a new agent type."""

    pass


class AgentTypeUpdate(BaseModel):
    """Schema for updating an existing agent type.

    All fields are optional to support partial updates.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated agent type name"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated description"
    )

    model_config = ConfigDict(from_attributes=True)


class AgentTypeResponse(AgentTypeBase):
    """Agent type schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique agent type identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the agent type was created"
    )

    model_config = ConfigDict(from_attributes=True)
