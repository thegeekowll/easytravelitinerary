"""
Pydantic schemas package.

This package contains all Pydantic V2 schemas for request/response validation.
"""

# Common schemas
from app.schemas.common import (
    PaginatedResponse,
    MessageResponse,
    ErrorResponse,
)

# User and authentication schemas
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserWithPermissions,
)

# Permission schemas
from app.schemas.permission import (
    PermissionBase,
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionAssignment,
)

# Agent type schemas
from app.schemas.agent_type import (
    AgentTypeBase,
    AgentTypeCreate,
    AgentTypeUpdate,
    AgentTypeResponse,
)

# Destination schemas
from app.schemas.destination import (
    DestinationBase,
    DestinationCreate,
    DestinationUpdate,
    DestinationResponse,
    DestinationWithImages,
    DestinationImageBase,
    DestinationImageCreate,
    DestinationImageUpdate,
    DestinationImageResponse,
)

# Accommodation schemas
from app.schemas.accommodation import (
    AccommodationBase,
    AccommodationCreate,
    AccommodationUpdate,
    AccommodationResponse,
    AccommodationWithDetails,
    AccommodationTypeBase,
    AccommodationTypeCreate,
    AccommodationTypeUpdate,
    AccommodationTypeResponse,
    AccommodationImageBase,
    AccommodationImageCreate,
    AccommodationImageUpdate,
    AccommodationImageResponse,
)

# Base tour schemas
from app.schemas.base_tour import (
    BaseTourBase,
    BaseTourCreate,
    BaseTourUpdate,
    BaseTourResponse,
    BaseTourWithDetails,
    BaseTourDayBase,
    BaseTourDayCreate,
    BaseTourDayUpdate,
    BaseTourDayResponse,
    BaseTourDayWithDestinations,
    TourTypeBase,
    TourTypeCreate,
    TourTypeUpdate,
    TourTypeResponse,
    BaseTourImageBase,
    BaseTourImageCreate,
    BaseTourImageUpdate,
    BaseTourImageResponse,
)

# Inclusion and exclusion schemas
from app.schemas.inclusion import (
    InclusionBase,
    InclusionCreate,
    InclusionUpdate,
    InclusionResponse,
)

from app.schemas.exclusion import (
    ExclusionBase,
    ExclusionCreate,
    ExclusionUpdate,
    ExclusionResponse,
)

# Destination combination schemas (2D auto-fill table)
from app.schemas.destination_combination import (
    DestinationCombinationBase,
    DestinationCombinationCreate,
    DestinationCombinationUpdate,
    DestinationCombinationResponse,
    DestinationCombinationWithDestinations,
    DestinationCombinationLookup,
)

# Itinerary schemas (most complex)
from app.schemas.itinerary import (
    # Traveler schemas
    TravelerBase,
    TravelerCreate,
    TravelerUpdate,
    TravelerResponse,
    # Itinerary day schemas
    ItineraryDayBase,
    ItineraryDayCreate,
    ItineraryDayUpdate,
    ItineraryDayResponse,
    # NOTE: ItineraryDayWithDetails removed - import directly when needed to avoid circular dependencies
    # Itinerary schemas
    ItineraryBase,
    ItineraryCreateChooseExisting,
    ItineraryCreateEditExisting,
    ItineraryCreateCustom,
    ItineraryUpdate,
    ItineraryResponse,
    # NOTE: ItineraryWithDetails and ItineraryPublicView removed - import directly when needed
    ItineraryStatusChange,
)

# Payment schemas
from app.schemas.payment import (
    PaymentRecordBase,
    PaymentRecordCreate,
    PaymentRecordUpdate,
    PaymentRecordResponse,
    PaymentSummary,
)

# Email schemas
from app.schemas.email import (
    EmailSendRequest,
    EmailLogResponse,
    EmailBulkSendRequest,
    EmailStatistics,
)

# Notification schemas
from app.schemas.notification import (
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationMarkAllRead,
    NotificationSummary,
)

# Company content and assets schemas
from app.schemas.company import (
    CompanyContentBase,
    CompanyContentCreate,
    CompanyContentUpdate,
    CompanyContentResponse,
    CompanyAssetBase,
    CompanyAssetCreate,
    CompanyAssetUpdate,
    CompanyAssetResponse,
)

__all__ = [
    # Common
    "PaginatedResponse",
    "MessageResponse",
    "ErrorResponse",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserWithPermissions",
    # Permission
    "PermissionBase",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionResponse",
    "PermissionAssignment",
    # Agent Type
    "AgentTypeBase",
    "AgentTypeCreate",
    "AgentTypeUpdate",
    "AgentTypeResponse",
    # Destination
    "DestinationBase",
    "DestinationCreate",
    "DestinationUpdate",
    "DestinationResponse",
    "DestinationWithImages",
    "DestinationImageBase",
    "DestinationImageCreate",
    "DestinationImageUpdate",
    "DestinationImageResponse",
    # Accommodation
    "AccommodationBase",
    "AccommodationCreate",
    "AccommodationUpdate",
    "AccommodationResponse",
    "AccommodationWithDetails",
    "AccommodationTypeBase",
    "AccommodationTypeCreate",
    "AccommodationTypeUpdate",
    "AccommodationTypeResponse",
    "AccommodationImageBase",
    "AccommodationImageCreate",
    "AccommodationImageUpdate",
    "AccommodationImageResponse",
    # Base Tour
    "BaseTourBase",
    "BaseTourCreate",
    "BaseTourUpdate",
    "BaseTourResponse",
    "BaseTourWithDetails",
    "BaseTourDayBase",
    "BaseTourDayCreate",
    "BaseTourDayUpdate",
    "BaseTourDayResponse",
    "BaseTourDayWithDestinations",
    "TourTypeBase",
    "TourTypeCreate",
    "TourTypeUpdate",
    "TourTypeResponse",
    "BaseTourImageBase",
    "BaseTourImageCreate",
    "BaseTourImageUpdate",
    "BaseTourImageResponse",
    # Inclusion/Exclusion
    "InclusionBase",
    "InclusionCreate",
    "InclusionUpdate",
    "InclusionResponse",
    "ExclusionBase",
    "ExclusionCreate",
    "ExclusionUpdate",
    "ExclusionResponse",
    # Destination Combination
    "DestinationCombinationBase",
    "DestinationCombinationCreate",
    "DestinationCombinationUpdate",
    "DestinationCombinationResponse",
    "DestinationCombinationWithDestinations",
    "DestinationCombinationLookup",
    # Itinerary
    "TravelerBase",
    "TravelerCreate",
    "TravelerUpdate",
    "TravelerResponse",
    "ItineraryDayBase",
    "ItineraryDayCreate",
    "ItineraryDayUpdate",
    "ItineraryDayResponse",
    # "ItineraryDayWithDetails",  # Removed to avoid circular dependency
    "ItineraryBase",
    "ItineraryCreateChooseExisting",
    "ItineraryCreateEditExisting",
    "ItineraryCreateCustom",
    "ItineraryUpdate",
    "ItineraryResponse",
    # "ItineraryWithDetails",  # Removed to avoid circular dependency
    # "ItineraryPublicView",  # Removed to avoid circular dependency
    "ItineraryStatusChange",
    # Payment
    "PaymentRecordBase",
    "PaymentRecordCreate",
    "PaymentRecordUpdate",
    "PaymentRecordResponse",
    "PaymentSummary",
    # Email
    "EmailSendRequest",
    "EmailLogResponse",
    "EmailBulkSendRequest",
    "EmailStatistics",
    # Notification
    "NotificationBase",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationMarkAllRead",
    "NotificationSummary",
    # Company
    "CompanyContentBase",
    "CompanyContentCreate",
    "CompanyContentUpdate",
    "CompanyContentResponse",
    "CompanyAssetBase",
    "CompanyAssetCreate",
    "CompanyAssetUpdate",
    "CompanyAssetResponse",
]
