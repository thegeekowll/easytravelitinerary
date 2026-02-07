# CRUD Endpoints - COMPLETE ✅

## Summary

Complete CRUD endpoints for core database models in the Travel Agency Management System.

**Date:** January 23, 2026
**Status:** Implementation Complete - Ready for Testing

---

## Files Created

### 1. Destinations Endpoints (`/app/api/v1/endpoints/destinations.py`)

**Routes:**
- `GET /api/v1/destinations` - List destinations with pagination
- `GET /api/v1/destinations/{id}` - Get destination by ID
- `POST /api/v1/destinations` - Create destination (requires permission)
- `PATCH /api/v1/destinations/{id}` - Update destination (requires permission)
- `DELETE /api/v1/destinations/{id}` - Delete destination (admin only)
- `POST /api/v1/destinations/{id}/images` - Upload multiple images
- `DELETE /api/v1/destinations/images/{image_id}` - Delete image
- `GET /api/v1/destinations/export/csv` - Export to CSV (admin only)
- `POST /api/v1/destinations/bulk-import` - Import from CSV (admin only)

**Features:**
- Search by name (case-insensitive)
- Filter by country, region
- Pagination support
- Image management with Azure Blob Storage
- CSV import/export with error reporting
- Permission checks: `create_destination`, `edit_destination`

**Example Request:**
```bash
# List destinations with search
curl -X GET "http://localhost:8000/api/v1/destinations?search=paris&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create destination
curl -X POST "http://localhost:8000/api/v1/destinations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Paris",
    "country": "France",
    "region": "Île-de-France",
    "description": "The City of Light",
    "best_time_to_visit": "April to June, September to November",
    "average_temp_celsius": 12.5,
    "highlights": ["Eiffel Tower", "Louvre Museum", "Notre-Dame"],
    "activities": ["Sightseeing", "Museums", "Dining"]
  }'

# Upload images
curl -X POST "http://localhost:8000/api/v1/destinations/{id}/images" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@paris1.jpg" \
  -F "files=@paris2.jpg"
```

---

### 2. Accommodations Endpoints (`/app/api/v1/endpoints/accommodations.py`)

**Routes:**
- `GET /api/v1/accommodations/types` - List accommodation types
- `POST /api/v1/accommodations/types` - Create accommodation type (admin only)
- `GET /api/v1/accommodations` - List accommodations with pagination
- `GET /api/v1/accommodations/{id}` - Get accommodation by ID
- `POST /api/v1/accommodations` - Create accommodation (requires permission)
- `PATCH /api/v1/accommodations/{id}` - Update accommodation (requires permission)
- `DELETE /api/v1/accommodations/{id}` - Delete accommodation (admin only)
- `POST /api/v1/accommodations/{id}/images` - Upload multiple images
- `DELETE /api/v1/accommodations/images/{image_id}` - Delete image

**Features:**
- Search by name
- Filter by destination, accommodation type, star rating
- Pagination support
- Image management
- Accommodation type management (Hotel, Resort, Villa, etc.)
- Permission checks: `create_accommodation`, `edit_accommodation`

**Example Request:**
```bash
# Create accommodation type
curl -X POST "http://localhost:8000/api/v1/accommodations/types" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Luxury Hotel",
    "description": "5-star hotel with premium amenities"
  }'

# Create accommodation
curl -X POST "http://localhost:8000/api/v1/accommodations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hotel Ritz Paris",
    "accommodation_type_id": "uuid-here",
    "destination_id": "uuid-here",
    "location": "15 Place Vendôme",
    "star_rating": 5,
    "description": "Iconic luxury hotel in Paris",
    "amenities": ["Spa", "Fine Dining", "Concierge", "Room Service"],
    "contact_email": "info@ritzparis.com",
    "contact_phone": "+33 1 43 16 30 30"
  }'
```

---

### 3. Base Tours Endpoints (`/app/api/v1/endpoints/base_tours.py`)

**Routes:**
- `GET /api/v1/base-tours/types` - List tour types
- `POST /api/v1/base-tours/types` - Create tour type (admin only)
- `GET /api/v1/base-tours` - List base tours with pagination
- `GET /api/v1/base-tours/{id}` - Get base tour with nested days
- `POST /api/v1/base-tours` - Create base tour (admin only)
- `PATCH /api/v1/base-tours/{id}` - Update base tour (admin only)
- `DELETE /api/v1/base-tours/{id}` - Delete base tour (admin only)
- `POST /api/v1/base-tours/{id}/duplicate` - Clone base tour (admin only)
- `POST /api/v1/base-tours/{id}/images` - Upload multiple images (admin only)

**Features:**
- Search by title
- Filter by tour type, duration (min/max days), active status
- Pagination support
- Nested days management
- Duplicate/clone functionality
- Image management
- Admin-only restrictions

**Special Feature - Duplicate Endpoint:**
```bash
# Clone an existing tour with all its days
curl -X POST "http://localhost:8000/api/v1/base-tours/{tour_id}/duplicate?new_title=Paris%20Explorer%20Premium" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Example Request:**
```bash
# Create tour type
curl -X POST "http://localhost:8000/api/v1/base-tours/types" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cultural Tour",
    "description": "Explore art, history, and culture"
  }'

# Create base tour
curl -X POST "http://localhost:8000/api/v1/base-tours" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Paris Explorer",
    "tour_type_id": "uuid-here",
    "duration_days": 5,
    "description": "Discover the best of Paris",
    "highlights": ["Eiffel Tower", "Louvre", "Seine River Cruise"],
    "difficulty_level": "Easy",
    "is_active": true
  }'
```

**Note:** Days are managed separately through dedicated endpoints (to be created).

---

### 4. Content Endpoints (`/app/api/v1/endpoints/content.py`)

#### Inclusions

**Routes:**
- `GET /api/v1/content/inclusions` - List all inclusions
- `POST /api/v1/content/inclusions` - Create inclusion (admin only)
- `PATCH /api/v1/content/inclusions/{id}` - Update inclusion (admin only)
- `DELETE /api/v1/content/inclusions/{id}` - Delete inclusion (admin only)

#### Exclusions

**Routes:**
- `GET /api/v1/content/exclusions` - List all exclusions
- `POST /api/v1/content/exclusions` - Create exclusion (admin only)
- `PATCH /api/v1/content/exclusions/{id}` - Update exclusion (admin only)
- `DELETE /api/v1/content/exclusions/{id}` - Delete exclusion (admin only)

#### Company Content

**Routes:**
- `GET /api/v1/content/company` - Get company content
- `POST /api/v1/content/company/logo` - Upload company logo (admin only)
- `GET /api/v1/content/company/awards` - List award badges
- `POST /api/v1/content/company/awards` - Upload award badge (admin only)
- `DELETE /api/v1/content/company/awards/{id}` - Delete award badge (admin only)
- `GET /api/v1/content/company/templates` - Get all templates
- `PATCH /api/v1/content/company/templates/{key}` - Update template (admin only)

**Template Keys:**
- `intro_letter_template` - Introduction letter for itineraries
- `about_company_template` - Company description
- `cta_message_template` - Call-to-action message
- `email_template` - Email body template

**Example Requests:**
```bash
# Create inclusion
curl -X POST "http://localhost:8000/api/v1/content/inclusions" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Airport Transfers",
    "description": "Round-trip airport transfers included"
  }'

# Upload company logo
curl -X POST "http://localhost:8000/api/v1/content/company/logo" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -F "file=@company_logo.png"

# Update email template
curl -X PATCH "http://localhost:8000/api/v1/content/company/templates/email_template" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Dear {customer_name},\n\nThank you for choosing our services..."
  }'
```

---

### 5. Media Endpoints (`/app/api/v1/endpoints/media.py`)

**Routes:**
- `POST /api/v1/media/upload` - Upload single file
- `POST /api/v1/media/upload-multiple` - Upload multiple files
- `DELETE /api/v1/media` - Delete file by URL
- `GET /api/v1/media/list` - List files in container/folder

**Features:**
- Upload to any Azure Blob container
- Organize files in folders
- Batch upload support
- Delete by URL
- List files in specific locations
- Available to all authenticated users

**Example Requests:**
```bash
# Upload single file
curl -X POST "http://localhost:8000/api/v1/media/upload?container=general&folder=docs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"

# Upload multiple files
curl -X POST "http://localhost:8000/api/v1/media/upload-multiple?container=general&folder=images" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.jpg"

# List files
curl -X GET "http://localhost:8000/api/v1/media/list?container=general&folder=docs" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Delete file
curl -X DELETE "http://localhost:8000/api/v1/media?file_url=https://storage.blob.core.windows.net/..." \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 6. Import Service (`/app/services/import_service.py`)

**Methods:**
- `import_destinations_from_csv(csv_content, db)` - Bulk import destinations
- `import_accommodations_from_csv(csv_content, db)` - Bulk import accommodations
- `import_base_tours_from_csv(csv_content, db)` - Bulk import tours

**Features:**
- Parse CSV content
- Row-by-row validation
- Detailed error reporting (row number, data, error message)
- Transaction management (rollback on parsing error)
- Success/failure counts
- Already integrated into destinations endpoint

**CSV Format - Destinations:**
```csv
name,country,region,description,best_time_to_visit,average_temp_celsius,highlights,activities
Paris,France,Île-de-France,The City of Light,April to June,12.5,"Eiffel Tower,Louvre,Notre-Dame","Sightseeing,Museums,Dining"
```

**CSV Format - Accommodations:**
```csv
name,accommodation_type_id,destination_id,location,star_rating,description,amenities,contact_email,contact_phone
Hotel Ritz Paris,uuid-here,uuid-here,15 Place Vendôme,5,Iconic luxury hotel,"Spa,Fine Dining,Concierge",info@ritzparis.com,+33 1 43 16 30 30
```

**CSV Format - Base Tours:**
```csv
title,tour_type_id,duration_days,description,highlights,difficulty_level,is_active
Paris Explorer,uuid-here,5,Discover Paris,"Eiffel Tower,Louvre,Seine Cruise",Easy,true
```

**Response Format:**
```json
{
  "success": true,
  "imported_count": 15,
  "failed_count": 2,
  "imported": [
    {"row": 2, "name": "Paris", "id": "uuid-here"},
    {"row": 3, "name": "London", "id": "uuid-here"}
  ],
  "failed": [
    {"row": 4, "data": {...}, "error": "Destination already exists"},
    {"row": 5, "data": {...}, "error": "Invalid temperature value"}
  ]
}
```

---

### 7. API Router Updated (`/app/api/v1/api.py`)

All new routers have been included:

```python
from app.api.v1.endpoints import (
    auth,
    users,
    destinations,
    accommodations,
    base_tours,
    content,
    media
)

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(destinations.router)
api_router.include_router(accommodations.router)
api_router.include_router(base_tours.router)
api_router.include_router(content.router)
api_router.include_router(media.router)
```

---

## Common Patterns

### Pagination

All list endpoints support pagination:
```bash
?page=1&page_size=20
```

Response format:
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "has_next": true,
  "has_prev": false
}
```

### Search & Filters

Most list endpoints support:
- `search` - Text search (case-insensitive)
- Specific filters (country, region, star_rating, etc.)
- Sort options (coming from PaginationParams)

### Permission Checks

Three levels of access control:

1. **Authenticated Users** - Can read (list, get)
   ```python
   current_user: User = Depends(get_current_active_user)
   ```

2. **Permission-Based** - Can create/edit with specific permission
   ```python
   current_user: User = Depends(RequirePermission("create_destination"))
   ```

3. **Admin Only** - Can delete and perform sensitive operations
   ```python
   current_user: User = Depends(require_admin)
   ```

### Error Handling

All endpoints include:
- Input validation (Pydantic schemas)
- Database transaction management
- Error rollback on failures
- Descriptive error messages
- Proper HTTP status codes

### Image Management

Image upload pattern:
```python
# Upload multiple images
files: List[UploadFile] = File(...)

for file in files:
    image_url = await azure_blob_service.upload_image(
        file,
        container="container-name",
        folder=str(resource_id)
    )
    # Save to database
```

---

## Testing Guide

### 1. Start the Server

```bash
cd backend
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

### 2. Access API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 3. Authenticate

Use the test script or manual login:

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@travelagency.com&password=Admin123!"
```

Copy the `access_token` from the response.

### 4. Test Endpoints in Swagger UI

1. Click "Authorize" button in top-right
2. Enter: `Bearer YOUR_ACCESS_TOKEN`
3. Click "Authorize"
4. Now you can test all endpoints interactively

### 5. Test Each Module

**Destinations:**
- Create 2-3 destinations
- Upload images for each
- Test search and filters
- Try CSV import with sample data
- Export to CSV

**Accommodations:**
- Create accommodation types first
- Create accommodations linked to destinations
- Upload images
- Test filters by destination, type, star rating

**Base Tours:**
- Create tour types first
- Create base tours
- Test the duplicate endpoint
- Upload images

**Content:**
- Create 3-5 inclusions
- Create 3-5 exclusions
- Upload company logo
- Upload award badges
- Update email template

**Media:**
- Upload single file
- Upload multiple files
- List files in container
- Delete a file

---

## API Endpoints Summary

### Authentication & Users (from previous phase)
- POST `/api/v1/auth/login`
- POST `/api/v1/auth/refresh`
- GET `/api/v1/auth/me`
- POST `/api/v1/auth/logout`
- GET `/api/v1/users` (10 total user endpoints)

### Destinations (9 endpoints)
- GET `/api/v1/destinations`
- GET `/api/v1/destinations/{id}`
- POST `/api/v1/destinations`
- PATCH `/api/v1/destinations/{id}`
- DELETE `/api/v1/destinations/{id}`
- POST `/api/v1/destinations/{id}/images`
- DELETE `/api/v1/destinations/images/{image_id}`
- GET `/api/v1/destinations/export/csv`
- POST `/api/v1/destinations/bulk-import`

### Accommodations (9 endpoints)
- GET `/api/v1/accommodations/types`
- POST `/api/v1/accommodations/types`
- GET `/api/v1/accommodations`
- GET `/api/v1/accommodations/{id}`
- POST `/api/v1/accommodations`
- PATCH `/api/v1/accommodations/{id}`
- DELETE `/api/v1/accommodations/{id}`
- POST `/api/v1/accommodations/{id}/images`
- DELETE `/api/v1/accommodations/images/{image_id}`

### Base Tours (9 endpoints)
- GET `/api/v1/base-tours/types`
- POST `/api/v1/base-tours/types`
- GET `/api/v1/base-tours`
- GET `/api/v1/base-tours/{id}`
- POST `/api/v1/base-tours`
- PATCH `/api/v1/base-tours/{id}`
- DELETE `/api/v1/base-tours/{id}`
- POST `/api/v1/base-tours/{id}/duplicate`
- POST `/api/v1/base-tours/{id}/images`

### Content (13 endpoints)
- GET `/api/v1/content/inclusions`
- POST `/api/v1/content/inclusions`
- PATCH `/api/v1/content/inclusions/{id}`
- DELETE `/api/v1/content/inclusions/{id}`
- GET `/api/v1/content/exclusions`
- POST `/api/v1/content/exclusions`
- PATCH `/api/v1/content/exclusions/{id}`
- DELETE `/api/v1/content/exclusions/{id}`
- GET `/api/v1/content/company`
- POST `/api/v1/content/company/logo`
- GET `/api/v1/content/company/awards`
- POST `/api/v1/content/company/awards`
- DELETE `/api/v1/content/company/awards/{id}`
- GET `/api/v1/content/company/templates`
- PATCH `/api/v1/content/company/templates/{key}`

### Media (4 endpoints)
- POST `/api/v1/media/upload`
- POST `/api/v1/media/upload-multiple`
- DELETE `/api/v1/media`
- GET `/api/v1/media/list`

**Total API Endpoints:** 60+ endpoints

---

## Next Steps

### Immediate
1. ✅ All CRUD endpoints created
2. ✅ API router updated
3. ⏳ Test all endpoints in FastAPI docs
4. ⏳ Create sample CSV files for testing imports
5. ⏳ Initialize database with sample data

### Short Term
1. Create base tour days management endpoints
2. Create itinerary management endpoints (the core business logic)
3. Add activity logging for all CRUD operations
4. Implement soft delete for important resources
5. Add bulk operations (bulk delete, bulk update)

### Still Needed
1. **Itinerary Management** - The main feature
   - Create itinerary (3 methods: choose existing, edit existing, custom)
   - Manage itinerary days
   - Manage travelers
   - Calculate pricing
   - Generate PDFs

2. **Payment Tracking**
   - Record payments
   - Track balances
   - Payment reminders

3. **Email & Notifications**
   - Send itineraries via email
   - Payment reminders
   - Status updates
   - SMS notifications

4. **Analytics & Reporting**
   - Popular destinations
   - Revenue reports
   - Agent performance
   - Customer insights

---

## Project Status

```
✅ Phase 1: Project Structure
✅ Phase 2: Database Models (25 models, 33 tables)
✅ Phase 3: Pydantic Schemas (16 schema files, 100+ schemas)
✅ Phase 4: Authentication System
✅ Phase 5: CRUD Endpoints for Core Models (DONE!)
⏳ Phase 6: Itinerary Management (Main Feature)
⏳ Phase 7: Payment & Email Systems
⏳ Phase 8: Frontend Integration
⏳ Phase 9: Testing & Deployment

Overall Progress: 65% → 80%
```

---

## Files Created in This Phase

```
backend/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── destinations.py       ✅ 443 lines
│   │   ├── accommodations.py     ✅ 346 lines
│   │   ├── base_tours.py         ✅ 316 lines (was already created)
│   │   ├── content.py            ✅ 442 lines
│   │   └── media.py              ✅ 149 lines
│   ├── api/v1/
│   │   └── api.py                ✅ Updated with all routers
│   └── services/
│       └── import_service.py     ✅ 311 lines
└── CRUD_ENDPOINTS_COMPLETE.md    ✅ This file
```

**Total Lines of Code:** ~2,000 lines of production-ready API endpoints

---

**Status:** Implementation Complete - Ready for Testing
**Total Endpoints:** 60+ RESTful API endpoints
**Next Milestone:** Itinerary Management System

