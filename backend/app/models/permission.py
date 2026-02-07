"""
Permission model for granular access control.
"""
from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Text, Index, Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.session import Base


# Association table for User-Permission many-to-many relationship
user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "granted_at",
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    ),
    Column(
        "granted_by_user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
)


class Permission(Base):
    """
    Permission model for fine-grained access control.

    Each permission represents a specific action that can be performed in the system.
    """
    __tablename__ = "permissions"

    # Primary Fields
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_permissions,
        primaryjoin="Permission.id == user_permissions.c.permission_id",
        secondaryjoin="User.id == user_permissions.c.user_id",
        back_populates="permissions",
        lazy="dynamic"
    )

    # Indexes
    __table_args__ = (
        Index("ix_permissions_category", "category"),
    )

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"

    def to_dict(self) -> dict:
        """Convert permission to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
        }


# Pre-defined permission names as constants
class PermissionNames:
    """Permission name constants."""
    # Itinerary permissions
    CREATE_ITINERARY = "create_itinerary"
    EDIT_ITINERARY = "edit_itinerary"
    DELETE_ITINERARY = "delete_itinerary"
    VIEW_ALL_ITINERARIES = "view_all_itineraries"
    ASSIGN_ITINERARIES = "assign_itineraries"
    SEND_ITINERARY_EMAIL = "send_email"
    GENERATE_ITINERARY_PDF = "generate_pdf"

    # Destination permissions
    ADD_DESTINATION = "add_destination"
    EDIT_DESTINATION = "edit_destination"
    DELETE_DESTINATION = "delete_destination"
    VIEW_DESTINATIONS = "view_destinations"

    # Accommodation permissions
    ADD_ACCOMMODATION = "add_accommodation"
    EDIT_ACCOMMODATION = "edit_accommodation"
    DELETE_ACCOMMODATION = "delete_accommodation"
    VIEW_ACCOMMODATIONS = "view_accommodations"

    # Tour Package permissions
    ADD_TOUR_PACKAGE = "add_tour_package"
    EDIT_TOUR_PACKAGE = "edit_tour_package"
    DELETE_TOUR_PACKAGE = "delete_tour_package"
    VIEW_TOUR_PACKAGES = "view_tour_packages"

    # 2D Table permissions
    EDIT_2D_TABLE = "edit_2d_table"
    VIEW_2D_TABLE = "view_2d_table"

    # User management permissions
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    MANAGE_PERMISSIONS = "manage_permissions"

    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    VIEW_ANALYTICS_REVENUE = "view_analytics_revenue"
    EXPORT_ANALYTICS = "export_analytics"

    # System permissions
    MANAGE_AGENT_TYPES = "manage_agent_types"
    MANAGE_ACCOMMODATION_TYPES = "manage_accommodation_types"
    MANAGE_TOUR_TYPES = "manage_tour_types"
    VIEW_ACTIVITY_LOGS = "view_activity_logs"


# Permission categories
class PermissionCategories:
    """Permission category constants."""
    ITINERARY = "itinerary"
    DESTINATION = "destination"
    ACCOMMODATION = "accommodation"
    TOUR_PACKAGE = "tour_package"
    USER_MANAGEMENT = "user_management"
    ANALYTICS = "analytics"
    SYSTEM = "system"
    TWO_D_TABLE = "2d_table"
