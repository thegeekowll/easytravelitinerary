"""
User-related Pydantic schemas.

This module contains schemas for user authentication, registration, and profile management.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from app.models.user import UserRoleEnum


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(
        ...,
        description="User's email address (must be unique)"
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's full name"
    )
    role: UserRoleEnum = Field(
        default=UserRoleEnum.CS_AGENT,
        description="User role: admin or cs_agent (customer service agent)"
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active"
    )
    phone_number: Optional[str] = Field(
        default=None,
        description="User's phone number"
    )
    profile_photo_url: Optional[str] = Field(
        default=None,
        description="URL to the user's profile photo"
    )
    position: Optional[str] = Field(
        default=None,
        description="User's job position or title"
    )

    model_config = ConfigDict(from_attributes=True)



class UserCreate(UserBase):
    """Schema for creating a new user.

    Requires password and optional permission assignments.
    """

    password: str = Field(
        ...,
        min_length=8,
        description="User password (min 8 characters, must meet complexity requirements)"
    )
    permission_ids: Optional[List[UUID]] = Field(
        default=None,
        description="List of permission IDs to assign to the user"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets complexity requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)

        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one digit, and one special character'
            )

        return v

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating an existing user.

    All fields are optional to support partial updates.
    """

    email: Optional[EmailStr] = Field(
        None,
        description="Updated email address"
    )
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated full name"
    )
    role: Optional[UserRoleEnum] = Field(
        None,
        description="Updated user role"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Updated active status"
    )
    phone_number: Optional[str] = Field(
        default=None,
        description="Updated phone number"
    )
    profile_photo_url: Optional[str] = Field(
        default=None,
        description="Updated profile photo URL"
    )
    position: Optional[str] = Field(
        default=None,
        description="Updated job position"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="New password (optional)"
    )
    permission_ids: Optional[List[UUID]] = Field(
        None,
        description="Updated list of permission IDs (replaces existing permissions)"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password meets complexity requirements."""
        if v is None:
            return v

        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)

        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one digit, and one special character'
            )

        return v

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    """User schema as stored in database.

    Includes database-generated fields and password hash.
    """

    id: UUID = Field(
        ...,
        description="Unique user identifier"
    )
    hashed_password: str = Field(
        ...,
        description="Hashed password (never sent to client)"
    )
    created_at: datetime = Field(
        ...,
        description="When the user account was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the user account was last updated"
    )
    last_login: Optional[datetime] = Field(
        None,
        description="When the user last logged in"
    )

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """User schema for API responses.

    Excludes sensitive fields like password hash.
    """

    id: UUID = Field(
        ...,
        description="Unique user identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the user account was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the user account was last updated"
    )
    last_login: Optional[datetime] = Field(
        None,
        description="When the user last logged in"
    )
    permission_count: Optional[int] = Field(
        None,
        description="Number of permissions assigned to this user"
    )

    model_config = ConfigDict(from_attributes=True)


class UserWithPermissions(UserResponse):
    """User response with full permission details.

    Used when detailed permission information is needed.
    """

    permissions: List['PermissionResponse'] = Field(
        default_factory=list,
        description="List of permissions assigned to this user"
    )

    model_config = ConfigDict(from_attributes=True)


# Import at the end to avoid circular imports
from app.schemas.permission import PermissionResponse
UserWithPermissions.model_rebuild()
