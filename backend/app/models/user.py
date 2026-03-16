"""
User model for authentication and user management.
"""
from datetime import datetime
from typing import List
from sqlalchemy import Boolean, String, DateTime, Enum as SQLEnum, Text, ForeignKey, Index, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import enum

from app.db.session import Base
from app.core.security import verify_password
from app.models.permission import user_permissions


class UserRoleEnum(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    CS_AGENT = "cs_agent"


class User(Base):
    """
    User model for authentication and authorization.

    Represents both admin and CS agent users in the system.
    """
    __tablename__ = "users"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Role and Status
    role: Mapped[UserRoleEnum] = mapped_column(
        SQLEnum(UserRoleEnum, name="user_role_enum"),
        nullable=False,
        default=UserRoleEnum.CS_AGENT
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Profile Information
    profile_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Agent Type (for CS Agents only)
    agent_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    agent_type: Mapped["AgentType"] = relationship(
        "AgentType",
        foreign_keys=[agent_type_id],
        back_populates="users",
        lazy="joined"
    )

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=user_permissions,
        primaryjoin="User.id == user_permissions.c.user_id",
        secondaryjoin="Permission.id == user_permissions.c.permission_id",
        back_populates="users",
        lazy="selectin"
    )

    itineraries_created: Mapped[List["Itinerary"]] = relationship(
        "Itinerary",
        foreign_keys="[Itinerary.created_by_user_id]",
        back_populates="creator",
        lazy="dynamic"
    )

    itineraries_assigned: Mapped[List["Itinerary"]] = relationship(
        "Itinerary",
        foreign_keys="[Itinerary.assigned_to_user_id]",
        back_populates="assigned_agent",
        lazy="dynamic"
    )

    activity_logs: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="user",
        lazy="dynamic"
    )

    destinations_created: Mapped[List["Destination"]] = relationship(
        "Destination",
        back_populates="creator",
        lazy="dynamic"
    )

    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        lazy="dynamic"
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_role", "role"),
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"

    def verify_password(self, password: str) -> bool:
        """
        Verify password against hashed password.

        Args:
            password: Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return verify_password(password, self.hashed_password)

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            permission_name: Name of the permission to check

        Returns:
            bool: True if user has the permission, False otherwise
        """
        # Admin has all permissions
        if self.role == UserRoleEnum.ADMIN:
            return True

        # Check user's assigned permissions
        return any(p.name == permission_name for p in self.permissions)

    def has_any_permission(self, permission_names: List[str]) -> bool:
        """
        Check if user has any of the specified permissions.

        Args:
            permission_names: List of permission names to check

        Returns:
            bool: True if user has any of the permissions
        """
        if self.role == UserRoleEnum.ADMIN:
            return True

        user_permissions = {p.name for p in self.permissions}
        return any(perm in user_permissions for perm in permission_names)

    def has_all_permissions(self, permission_names: List[str]) -> bool:
        """
        Check if user has all of the specified permissions.

        Args:
            permission_names: List of permission names to check

        Returns:
            bool: True if user has all permissions
        """
        if self.role == UserRoleEnum.ADMIN:
            return True

        user_permissions = {p.name for p in self.permissions}
        return all(perm in user_permissions for perm in permission_names)

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRoleEnum.ADMIN

    @property
    def is_cs_agent(self) -> bool:
        """Check if user is a CS agent."""
        return self.role == UserRoleEnum.CS_AGENT

    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding password)."""
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "profile_photo_url": self.profile_photo_url,
            "phone_number": self.phone_number,
            "address": self.address,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "agent_type": self.agent_type.name if self.agent_type else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
