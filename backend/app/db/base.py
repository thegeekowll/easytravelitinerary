"""
Import all models here for Alembic to detect them.
"""
from app.db.session import Base

# Phase 2.1 Models
from app.models.user import User, UserRoleEnum
from app.models.permission import Permission, user_permissions
from app.models.agent_type import AgentType
from app.models.destination import Destination, DestinationImage, ImageTypeEnum
from app.models.destination_combination import DestinationCombination
from app.models.accommodation import Accommodation, AccommodationType, AccommodationImage
from app.models.base_tour import (
    BaseTour, BaseTourDay, BaseTourImage, TourType,
    base_tour_inclusions, base_tour_exclusions, base_tour_day_destinations
)
from app.models.inclusion_exclusion import Inclusion, Exclusion
from app.models.activity_log import ActivityLog

# Phase 2.2 Models
from app.models.itinerary import (
    Itinerary, ItineraryDay, Traveler,
    itinerary_day_destinations, itinerary_featured_accommodations,
    itinerary_inclusions, itinerary_exclusions
)
from app.models.payment import PaymentRecord
from app.models.email_log import EmailLog
from app.models.notification import Notification
from app.models.company import CompanyContent, CompanyAsset

__all__ = [
    "Base",
    # Phase 2.1
    "User", "UserRoleEnum",
    "Permission", "user_permissions",
    "AgentType",
    "Destination", "DestinationImage", "ImageTypeEnum",
    "DestinationCombination",
    "Accommodation", "AccommodationType", "AccommodationImage",
    "BaseTour", "BaseTourDay", "BaseTourImage", "TourType",
    "base_tour_inclusions", "base_tour_exclusions", "base_tour_day_destinations",
    "Inclusion", "Exclusion",
    "ActivityLog",
    # Phase 2.2
    "Itinerary", "ItineraryDay", "Traveler",
    "itinerary_day_destinations", "itinerary_featured_accommodations",
    "itinerary_inclusions", "itinerary_exclusions",
    "PaymentRecord",
    "EmailLog",
    "EmailLog",
    "Notification",
    "CompanyContent", "CompanyAsset",
]
