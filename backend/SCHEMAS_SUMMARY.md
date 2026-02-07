# Pydantic Schemas Summary

**Phase 3: COMPLETE** ✅

All Pydantic V2 schemas have been created for the Travel Agency Management System.

## Overview

Created **16 schema files** containing **100+ schema classes** with:
- ✅ Pydantic V2 syntax (`ConfigDict`, `Field`, etc.)
- ✅ Proper validation (EmailStr, constr, field_validator)
- ✅ Field descriptions with examples
- ✅ `ConfigDict(from_attributes=True)` for ORM compatibility
- ✅ Proper typing (Optional, List, Dict)
- ✅ Support for nested relationships
- ✅ 3 creation methods for itineraries

---

## Files Created

### 1. `/backend/app/schemas/common.py`
**Purpose:** Generic response schemas used across the application

**Schemas:**
- `PaginatedResponse[T]` - Generic pagination wrapper with metadata
- `MessageResponse` - Simple success messages
- `ErrorResponse` - Error details with optional error codes

**Key Features:**
- Generic TypeVar for pagination
- Reusable across all list endpoints

---

### 2. `/backend/app/schemas/user.py`
**Purpose:** User authentication, registration, and profile management

**Schemas:**
- `UserBase` - Base schema with common fields
- `UserCreate` - Creating new users with password validation
- `UserUpdate` - Partial updates
- `UserInDB` - Database representation (includes hashed_password)
- `UserResponse` - API responses (excludes password)
- `UserWithPermissions` - User with nested permission details

**Key Features:**
- Password complexity validation (min 8 chars, uppercase, lowercase, digit, special)
- Role-based access (admin, cs_agent)
- Permission tracking

**Example Usage:**
```python
# Create user
user_data = UserCreate(
    email="agent@travel.com",
    full_name="John Smith",
    password="SecurePass123!",
    role="cs_agent"
)
```

---

### 3. `/backend/app/schemas/permission.py`
**Purpose:** Granular permission management

**Schemas:**
- `PermissionBase` - Permission definition
- `PermissionCreate` - Creating new permissions
- `PermissionUpdate` - Updating permissions
- `PermissionResponse` - API responses
- `PermissionAssignment` - Assigning permissions to users

**Key Features:**
- Category-based grouping
- Used for fine-grained access control

---

### 4. `/backend/app/schemas/agent_type.py`
**Purpose:** Travel agent specialization categories

**Schemas:**
- `AgentTypeBase` - Agent specialization (e.g., "Europe Specialist")
- `AgentTypeCreate` - Creating new types
- `AgentTypeUpdate` - Updating types
- `AgentTypeResponse` - API responses

**Key Features:**
- Categorizes agents by expertise
- Used for assignment logic

---

### 5. `/backend/app/schemas/inclusion.py` & `/backend/app/schemas/exclusion.py`
**Purpose:** Tour/itinerary inclusions and exclusions

**Schemas (each file):**
- `Base` - Description and category
- `Create` - Adding new items
- `Update` - Modifying items
- `Response` - API responses

**Key Features:**
- Category-based organization (Transport, Meals, Accommodation)
- Reusable across tours and itineraries

**Example:**
```python
inclusion = InclusionCreate(
    description="Airport transfers included",
    category="Transport"
)
```

---

### 6. `/backend/app/schemas/destination.py`
**Purpose:** Destinations and their images

**Schemas:**
- `DestinationBase` - Name, country, region, GPS, timezone
- `DestinationCreate` - Creating destinations
- `DestinationUpdate` - Updating destinations
- `DestinationResponse` - Basic response
- `DestinationWithImages` - Response with nested images
- `DestinationImageBase/Create/Update/Response` - Image schemas

**Key Features:**
- GPS coordinate validation (latitude/longitude format)
- JSONB fields for attractions and travel_tips
- Nested image relationships
- Timezone support

**Example:**
```python
destination = DestinationCreate(
    name="Paris, France",
    country="France",
    region="Île-de-France",
    gps_coordinates="48.8566,2.3522",
    timezone="Europe/Paris",
    attractions={"landmarks": ["Eiffel Tower", "Louvre"]},
    travel_tips={"currency": "EUR", "language": "French"}
)
```

---

### 7. `/backend/app/schemas/accommodation.py`
**Purpose:** Accommodations, types, and images

**Schemas:**
- `AccommodationTypeBase/Create/Update/Response` - Hotel types
- `AccommodationBase` - Name, address, rating, amenities
- `AccommodationCreate` - Creating accommodations
- `AccommodationUpdate` - Updating accommodations
- `AccommodationResponse` - Basic response
- `AccommodationWithDetails` - Response with type and images
- `AccommodationImageBase/Create/Update/Response` - Image schemas

**Key Features:**
- Star rating validation (0.0 to 5.0)
- GPS coordinate validation
- JSONB fields for amenities and contact_info
- Check-in/check-out times
- Linked to destination and accommodation type

**Example:**
```python
accommodation = AccommodationCreate(
    name="Grand Hotel Paris",
    accommodation_type_id=uuid4(),
    destination_id=uuid4(),
    star_rating=4.5,
    amenities={"facilities": ["WiFi", "Pool", "Spa"]},
    contact_info={"phone": "+33 1 23 45 67 89"}
)
```

---

### 8. `/backend/app/schemas/base_tour.py`
**Purpose:** Base tour templates (reusable tour packages)

**Schemas:**
- `TourTypeBase/Create/Update/Response` - Tour categories
- `BaseTourBase` - Title, duration, description, highlights
- `BaseTourCreate` - Creating tour templates
- `BaseTourUpdate` - Updating templates
- `BaseTourResponse` - Basic response
- `BaseTourWithDetails` - Full response with days, images, inclusions/exclusions
- `BaseTourDayBase/Create/Update/Response/WithDestinations` - Day schemas
- `BaseTourImageBase/Create/Update/Response` - Image schemas

**Key Features:**
- Multi-day tour structure
- Nested relationships (days → destinations)
- Inclusions and exclusions
- Tour difficulty levels
- Active/inactive status

**Example:**
```python
tour = BaseTourCreate(
    title="European Grand Tour - 14 Days",
    tour_type_id=uuid4(),
    duration_days=14,
    difficulty_level="Moderate"
)

day = BaseTourDayCreate(
    base_tour_id=tour_id,
    day_number=1,
    title="Arrival in Paris",
    description="Airport transfer and city orientation",
    destination_ids=[paris_id],
    meals_included="Dinner"
)
```

---

### 9. `/backend/app/schemas/destination_combination.py`
**Purpose:** 2D lookup table for auto-filling itinerary descriptions

**Schemas:**
- `DestinationCombinationBase` - Two destinations with combined content
- `DestinationCombinationCreate` - Adding combinations
- `DestinationCombinationUpdate` - Updating combinations
- `DestinationCombinationResponse` - API response
- `DestinationCombinationWithDestinations` - Response with full destination objects
- `DestinationCombinationLookup` - Query schema for auto-fill

**Key Features:**
- **Critical for auto-fill feature**
- Stores pre-written content for destination pairs
- Travel time and transportation mode
- Used when agents select 2+ destinations for a day

**Example:**
```python
combo = DestinationCombinationCreate(
    destination1_id=paris_id,
    destination2_id=versailles_id,
    combined_description="Journey from Paris to Versailles to explore the Palace",
    combined_activities="Palace tour, Gardens, Hall of Mirrors",
    travel_time_minutes=45,
    transportation_mode="Train (RER C)"
)

# Later, when creating itinerary day with both destinations:
# System looks up this combination and auto-fills description/activities
```

---

### 10. `/backend/app/schemas/itinerary.py` 🌟
**Purpose:** Main itinerary system (MOST COMPLEX FILE)

**Schemas:**

**Travelers:**
- `TravelerBase/Create/Update/Response` - Passenger information

**Itinerary Days:**
- `ItineraryDayBase` - Day number, description, activities
- `ItineraryDayCreate` - Creating days with destination IDs
- `ItineraryDayUpdate` - Updating days
- `ItineraryDayResponse` - Basic response
- `ItineraryDayWithDetails` - Response with destinations and accommodation

**Itineraries:**
- `ItineraryBase` - Common fields (client info, dates, pricing)
- `ItineraryCreateChooseExisting` - **Method 1:** Use base tour as-is
- `ItineraryCreateEditExisting` - **Method 2:** Start from base tour, allow edits
- `ItineraryCreateCustom` - **Method 3:** Fully custom from scratch
- `ItineraryUpdate` - Partial updates
- `ItineraryResponse` - Basic response with unique_code
- `ItineraryWithDetails` - Full response with all nested data
- `ItineraryPublicView` - Public client view (via unique_code URL)
- `ItineraryStatusChange` - Status workflow

**Key Features:**
- **3 Creation Methods:**
  1. `choose_existing` - Quick creation from base tour
  2. `edit_existing` - Modify base tour before saving
  3. `custom` - Build from scratch
- Date validation (return > departure)
- Currency validation (ISO 4217)
- Auto-fill tracking (`is_description_custom`, `is_activity_custom`)
- Unique 12-character code for public URLs
- Status workflow (draft → sent → confirmed → completed)
- Payment status tracking
- Full audit trail (created_by, assigned_agent)

**Example Usage:**

```python
# Method 1: Choose existing base tour
itinerary = ItineraryCreateChooseExisting(
    creation_method="choose_existing",
    base_tour_id=europe_tour_id,
    tour_title="European Tour - Smith Family",
    client_name="John Smith",
    client_email="john@example.com",
    departure_date="2024-06-15",
    return_date="2024-06-28",
    number_of_travelers=4
)

# Method 2: Edit existing base tour
itinerary = ItineraryCreateEditExisting(
    creation_method="edit_existing",
    base_tour_id=europe_tour_id,
    # ... same base fields ...
    days=[  # Custom modifications
        ItineraryDayCreate(
            day_number=1,
            destination_ids=[paris_id],
            description="Custom arrival day"
        )
    ],
    inclusion_ids=[custom_inclusion_id]
)

# Method 3: Fully custom
itinerary = ItineraryCreateCustom(
    creation_method="custom",
    # ... base fields ...
    days=[
        ItineraryDayCreate(
            day_number=1,
            destination_ids=[paris_id, versailles_id],  # Auto-fill triggers here
            accommodation_id=hotel_id
        )
    ]
)
```

---

### 11. `/backend/app/schemas/payment.py`
**Purpose:** Payment tracking and records

**Schemas:**
- `PaymentRecordBase` - Amount, currency, method, status
- `PaymentRecordCreate` - Recording payments
- `PaymentRecordUpdate` - Updating payment status
- `PaymentRecordResponse` - API response
- `PaymentSummary` - Aggregated payment stats

**Key Features:**
- Multiple payment methods (credit_card, bank_transfer, cash, check, other)
- Payment statuses (pending, completed, failed, refunded)
- Currency validation (ISO 4217)
- Transaction ID tracking
- Payment date tracking

**Example:**
```python
payment = PaymentRecordCreate(
    itinerary_id=itinerary_id,
    amount=2500.00,
    currency="USD",
    payment_method="credit_card",
    payment_status="completed",
    transaction_id="txn_1234567890"
)
```

---

### 12. `/backend/app/schemas/email.py`
**Purpose:** Email sending and logging

**Schemas:**
- `EmailSendRequest` - Sending emails with templates
- `EmailLogResponse` - Email delivery tracking
- `EmailBulkSendRequest` - Bulk email sending
- `EmailStatistics` - Email engagement metrics

**Key Features:**
- SendGrid integration support
- Template support with dynamic data
- CC/BCC support
- Attachment handling
- Delivery status tracking (sent, delivered, failed, bounced)
- Open and click tracking

**Example:**
```python
email = EmailSendRequest(
    to_email="client@example.com",
    to_name="John Smith",
    subject="Your European Tour Itinerary",
    body_text="Here is your custom itinerary...",
    body_html="<h1>Your Itinerary</h1>...",
    itinerary_id=itinerary_id,
    template_id="d-sendgrid-template-id",
    template_data={"customer_name": "John", "tour_name": "European Tour"}
)
```

---

### 13. `/backend/app/schemas/notification.py`
**Purpose:** System notifications for users

**Schemas:**
- `NotificationBase` - Title, message, type, priority
- `NotificationCreate` - Creating notifications
- `NotificationUpdate` - Marking as read
- `NotificationResponse` - API response
- `NotificationMarkAllRead` - Bulk mark as read
- `NotificationSummary` - Unread counts by type

**Key Features:**
- Notification types (arrival_alert, payment_reminder, assignment, system_alert, custom)
- Priority levels (low, normal, high, urgent)
- Read/unread tracking
- Related itinerary linking

**Example:**
```python
notification = NotificationCreate(
    user_id=agent_id,
    notification_type="arrival_alert",
    title="Client Arrival Tomorrow",
    message="John Smith arrives tomorrow for European Tour",
    related_itinerary_id=itinerary_id,
    priority="high"
)
```

---

### 14. `/backend/app/schemas/company.py`
**Purpose:** Company branding and assets

**Schemas:**
- `CompanyContentBase/Create/Update/Response` - Text content (taglines, legal text)
- `CompanyAssetBase/Create/Update/Response` - Digital assets (logos, images)

**Key Features:**
- Key-value content storage
- Asset metadata (MIME type, dimensions, file size)
- Category-based organization
- Active/inactive status

**Example:**
```python
content = CompanyContentCreate(
    content_key="company_tagline",
    content_value="Creating Unforgettable Journeys Since 1995",
    content_type="text",
    category="branding"
)

asset = CompanyAssetCreate(
    asset_key="logo_primary",
    asset_url="https://storage.example.com/logo.png",
    asset_type="image",
    mime_type="image/png",
    dimensions={"width": 1200, "height": 400}
)
```

---

### 15. `/backend/app/schemas/__init__.py`
**Purpose:** Central export point for all schemas

**Exports:** 100+ schema classes organized by category

**Usage:**
```python
from app.schemas import (
    UserCreate,
    ItineraryCreateCustom,
    PaginatedResponse,
    # ... all other schemas
)
```

---

## Schema Patterns

### Base → Create → Update → Response

All entity schemas follow this pattern:

1. **Base** - Common fields shared across operations
2. **Create** - Required fields for creation (extends Base)
3. **Update** - Optional fields for partial updates
4. **Response** - What API returns (adds id, timestamps)

### Nested Relationships

Complex schemas include nested data:
- `DestinationWithImages` - Destination + images[]
- `AccommodationWithDetails` - Accommodation + type + images[]
- `BaseTourWithDetails` - Tour + days[] + images[] + inclusions[] + exclusions[]
- `ItineraryWithDetails` - Itinerary + days[] + travelers[] + inclusions[] + exclusions[]

To avoid circular imports:
```python
# Import at end of file
from app.schemas.destination import DestinationResponse
ItineraryDayWithDetails.model_rebuild()
```

---

## Validation Examples

### Password Validation
```python
@field_validator('password')
@classmethod
def validate_password_strength(cls, v: str) -> str:
    # Min 8 chars, uppercase, lowercase, digit, special char
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters')
    # ... complexity checks
    return v
```

### GPS Coordinates
```python
@field_validator('gps_coordinates')
@classmethod
def validate_gps_format(cls, v: Optional[str]) -> Optional[str]:
    # Format: "latitude,longitude"
    # Lat: -90 to 90, Lon: -180 to 180
    parts = v.split(',')
    lat, lon = float(parts[0]), float(parts[1])
    # ... range validation
    return v
```

### Date Validation
```python
@field_validator('return_date')
@classmethod
def validate_dates(cls, v: date, info) -> date:
    if v <= info.data['departure_date']:
        raise ValueError('return_date must be after departure_date')
    return v
```

---

## Usage in FastAPI Routes

### Example: Create Itinerary Endpoint

```python
from fastapi import APIRouter, Depends
from app.schemas import ItineraryCreateCustom, ItineraryWithDetails

router = APIRouter()

@router.post("/itineraries/custom", response_model=ItineraryWithDetails)
async def create_custom_itinerary(
    itinerary: ItineraryCreateCustom,
    db: Session = Depends(get_db)
):
    # Pydantic automatically validates:
    # - Email format
    # - Date logic (return > departure)
    # - Currency code
    # - Required fields

    # Create itinerary in database
    db_itinerary = Itinerary(**itinerary.model_dump())
    db.add(db_itinerary)
    db.commit()

    # Pydantic serializes response with ConfigDict(from_attributes=True)
    return db_itinerary
```

### Example: Pagination

```python
from app.schemas import PaginatedResponse, DestinationResponse

@router.get("/destinations", response_model=PaginatedResponse[DestinationResponse])
async def list_destinations(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    total = db.query(Destination).count()
    destinations = db.query(Destination).offset((page-1)*page_size).limit(page_size).all()

    return PaginatedResponse(
        items=destinations,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
        has_next=page * page_size < total,
        has_prev=page > 1
    )
```

---

## Statistics

- **Total Schema Files:** 16
- **Total Schema Classes:** 100+
- **Lines of Code:** ~3,500
- **Covered Models:** 25 SQLAlchemy models
- **Database Tables:** 33 tables

---

## Next Steps

With all schemas complete, the next phases are:

**Phase 4: API Endpoints (CRUD Operations)**
- Create FastAPI routers for each resource
- Implement CRUD operations using schemas
- Add authentication and authorization
- Query parameters and filtering

**Phase 5: Business Logic**
- Auto-fill logic for destination combinations
- Itinerary creation workflows
- Email sending integration
- Notification generation

**Phase 6: Testing**
- Unit tests for schemas
- Integration tests for endpoints
- Test 3 itinerary creation methods

---

## Files Summary

```
backend/app/schemas/
├── __init__.py                    # Central exports (7KB)
├── common.py                      # Generic responses (2KB)
├── user.py                        # User & auth (7KB)
├── permission.py                  # Permissions (3KB)
├── agent_type.py                  # Agent categories (2KB)
├── inclusion.py                   # Tour inclusions (2KB)
├── exclusion.py                   # Tour exclusions (2KB)
├── destination.py                 # Destinations + images (9KB)
├── accommodation.py               # Accommodations + types + images (12KB)
├── base_tour.py                   # Tour templates + days + images (12KB)
├── destination_combination.py     # 2D auto-fill table (5KB)
├── itinerary.py                   # Itineraries + days + travelers (18KB) ⭐
├── payment.py                     # Payment records (6KB)
├── email.py                       # Email sending/logging (7KB)
├── notification.py                # Notifications (4KB)
└── company.py                     # Company content/assets (7KB)

Total: ~95KB of schema code
```

---

## Configuration Notes

All schemas use:
```python
from pydantic import BaseModel, Field, ConfigDict

class MySchema(BaseModel):
    field: str = Field(..., description="...", examples=["..."])

    model_config = ConfigDict(from_attributes=True)
```

This enables:
- ORM model → Pydantic schema conversion
- Automatic validation on assignment
- JSON serialization
- OpenAPI documentation generation

---

**Status: Phase 3 Complete ✅**

All Pydantic schemas created successfully with proper validation, typing, and documentation.
Ready for API endpoint development (Phase 4).
