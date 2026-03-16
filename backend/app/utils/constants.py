"""
Application constants and enums.
"""
from enum import Enum


class RoleEnum(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    CS_AGENT = "cs_agent"
    PUBLIC = "public"


class ItineraryStatusEnum(str, Enum):
    """Itinerary status enumeration."""
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatusEnum(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class NotificationTypeEnum(str, Enum):
    """Notification type enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ARRIVAL_ALERT = "arrival_alert"


class NotificationStatusEnum(str, Enum):
    """Notification status enumeration."""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class AnalyticsEventTypeEnum(str, Enum):
    """Analytics event type enumeration."""
    PAGE_VIEW = "page_view"
    ITINERARY_CREATED = "itinerary_created"
    ITINERARY_UPDATED = "itinerary_updated"
    ITINERARY_VIEWED = "itinerary_viewed"
    PDF_GENERATED = "pdf_generated"
    EMAIL_SENT = "email_sent"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"


class ItineraryCreationMethodEnum(str, Enum):
    """Itinerary creation method enumeration."""
    TEMPLATE = "template"
    CUSTOM = "custom"
    QUICK = "quick"


class AccommodationTypeEnum(str, Enum):
    """Accommodation type enumeration."""
    HOTEL = "hotel"
    RESORT = "resort"
    GUESTHOUSE = "guesthouse"
    APARTMENT = "apartment"
    VILLA = "villa"
    HOMESTAY = "homestay"
    CAMP = "camp"
    OTHER = "other"


class MealPlanEnum(str, Enum):
    """Meal plan enumeration."""
    ROOM_ONLY = "room_only"
    BREAKFAST = "breakfast"
    HALF_BOARD = "half_board"  # Breakfast + Dinner
    FULL_BOARD = "full_board"  # Breakfast + Lunch + Dinner
    ALL_INCLUSIVE = "all_inclusive"


# Permission constants
class Permissions:
    """Permission codes."""
    # User permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"

    # Itinerary permissions
    ITINERARY_CREATE = "itinerary:create"
    ITINERARY_READ = "itinerary:read"
    ITINERARY_UPDATE = "itinerary:update"
    ITINERARY_DELETE = "itinerary:delete"
    ITINERARY_LIST = "itinerary:list"
    ITINERARY_GENERATE_PDF = "itinerary:generate_pdf"
    ITINERARY_SEND_EMAIL = "itinerary:send_email"

    # Package permissions
    PACKAGE_CREATE = "package:create"
    PACKAGE_READ = "package:read"
    PACKAGE_UPDATE = "package:update"
    PACKAGE_DELETE = "package:delete"
    PACKAGE_LIST = "package:list"

    # Destination permissions
    DESTINATION_CREATE = "destination:create"
    DESTINATION_READ = "destination:read"
    DESTINATION_UPDATE = "destination:update"
    DESTINATION_DELETE = "destination:delete"
    DESTINATION_LIST = "destination:list"

    # Accommodation permissions
    ACCOMMODATION_CREATE = "accommodation:create"
    ACCOMMODATION_READ = "accommodation:read"
    ACCOMMODATION_UPDATE = "accommodation:update"
    ACCOMMODATION_DELETE = "accommodation:delete"
    ACCOMMODATION_LIST = "accommodation:list"

    # Analytics permissions
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"

    # System permissions
    SYSTEM_SETTINGS = "system:settings"
    ROLE_MANAGE = "role:manage"
    PERMISSION_MANAGE = "permission:manage"


# Default permissions by role
DEFAULT_ROLE_PERMISSIONS = {
    RoleEnum.ADMIN: [
        # Full access to everything
        Permissions.USER_CREATE,
        Permissions.USER_READ,
        Permissions.USER_UPDATE,
        Permissions.USER_DELETE,
        Permissions.USER_LIST,
        Permissions.ITINERARY_CREATE,
        Permissions.ITINERARY_READ,
        Permissions.ITINERARY_UPDATE,
        Permissions.ITINERARY_DELETE,
        Permissions.ITINERARY_LIST,
        Permissions.ITINERARY_GENERATE_PDF,
        Permissions.ITINERARY_SEND_EMAIL,
        Permissions.PACKAGE_CREATE,
        Permissions.PACKAGE_READ,
        Permissions.PACKAGE_UPDATE,
        Permissions.PACKAGE_DELETE,
        Permissions.PACKAGE_LIST,
        Permissions.DESTINATION_CREATE,
        Permissions.DESTINATION_READ,
        Permissions.DESTINATION_UPDATE,
        Permissions.DESTINATION_DELETE,
        Permissions.DESTINATION_LIST,
        Permissions.ACCOMMODATION_CREATE,
        Permissions.ACCOMMODATION_READ,
        Permissions.ACCOMMODATION_UPDATE,
        Permissions.ACCOMMODATION_DELETE,
        Permissions.ACCOMMODATION_LIST,
        Permissions.ANALYTICS_VIEW,
        Permissions.ANALYTICS_EXPORT,
        Permissions.SYSTEM_SETTINGS,
        Permissions.ROLE_MANAGE,
        Permissions.PERMISSION_MANAGE,
    ],
    RoleEnum.CS_AGENT: [
        # Can manage itineraries, packages, and view data
        Permissions.ITINERARY_CREATE,
        Permissions.ITINERARY_READ,
        Permissions.ITINERARY_UPDATE,
        Permissions.ITINERARY_LIST,
        Permissions.ITINERARY_GENERATE_PDF,
        Permissions.ITINERARY_SEND_EMAIL,
        Permissions.PACKAGE_READ,
        Permissions.PACKAGE_LIST,
        Permissions.DESTINATION_READ,
        Permissions.DESTINATION_LIST,
        Permissions.ACCOMMODATION_READ,
        Permissions.ACCOMMODATION_LIST,
        Permissions.ANALYTICS_VIEW,
    ],
    RoleEnum.PUBLIC: [
        # Limited read access
        Permissions.ITINERARY_READ,
    ],
}


# File upload constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS

# Date format constants
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

# Pagination constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Cache TTL (in seconds)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour
CACHE_TTL_DAY = 86400  # 24 hours
