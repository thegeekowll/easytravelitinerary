"""
SQLAlchemy models for the Itinerary Builder Platform.

This module exports all database models for use throughout the application.
"""

from app.models.user import User, UserRoleEnum
from app.models.permission import Permission, user_permissions, PermissionNames, PermissionCategories
from app.models.agent_type import AgentType
from app.models.destination import Destination, DestinationImage, ImageTypeEnum
from app.models.destination_combination import DestinationCombination
from app.models.accommodation import (
    Accommodation,
    AccommodationType,
    AccommodationLevel,
    AccommodationImage
)
from app.models.base_tour import (
    BaseTour,
    BaseTourDay,
    BaseTourImage,
    TourType,
    base_tour_inclusions,
    base_tour_exclusions,
    base_tour_day_destinations
)
from app.models.inclusion_exclusion import (
    Inclusion,
    Exclusion,
    InclusionCategories,
    ExclusionCategories
)
from app.models.activity_log import ActivityLog, ActivityActions, EntityTypes

# Phase 2.2: Itinerary Models
from app.models.itinerary import (
    Itinerary,
    ItineraryDay,
    Traveler,
    ItineraryStatusEnum,
    CreationMethodEnum,
    itinerary_day_destinations,
    itinerary_featured_accommodations,
    itinerary_inclusions,
    itinerary_exclusions
)
from app.models.payment import PaymentRecord, PaymentStatusEnum
from app.models.email_log import EmailLog, DeliveryStatusEnum
from app.models.notification import Notification, NotificationTypeEnum, PriorityEnum
from app.models.company import CompanyContent, CompanyAsset, AssetTypeEnum

__all__ = [
    # User and Authentication
    "User",
    "UserRoleEnum",
    "Permission",
    "user_permissions",
    "PermissionNames",
    "PermissionCategories",
    "AgentType",

    # Destinations
    "Destination",
    "DestinationImage",
    "ImageTypeEnum",
    "DestinationCombination",

    # Accommodations
    "Accommodation",
    "AccommodationType",
    "AccommodationLevel",
    "AccommodationImage",

    # Base Tours
    "BaseTour",
    "BaseTourDay",
    "BaseTourImage",
    "TourType",
    "base_tour_inclusions",
    "base_tour_exclusions",
    "base_tour_day_destinations",

    # Inclusions and Exclusions
    "Inclusion",
    "Exclusion",
    "InclusionCategories",
    "ExclusionCategories",

    # Activity Logs (General)
    "ActivityLog",
    "ActivityActions",
    "EntityTypes",

    # Itineraries (Phase 2.2)
    "Itinerary",
    "ItineraryDay",
    "Traveler",
    "ItineraryStatusEnum",
    "CreationMethodEnum",
    "itinerary_day_destinations",
    "itinerary_featured_accommodations",
    "itinerary_inclusions",
    "itinerary_exclusions",

    # Payment
    "PaymentRecord",
    "PaymentStatusEnum",

    # Email
    "EmailLog",
    "DeliveryStatusEnum",

    # Notifications
    "Notification",
    "NotificationTypeEnum",
    "PriorityEnum",

    # Company
    "CompanyContent",
    "CompanyAsset",
    "AssetTypeEnum",
]
