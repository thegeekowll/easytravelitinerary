# Docker Setup Issues Found & Fixed

## Date: 2026-01-24

---

## Issues Found During Docker Setup

### 1. ✅ FIXED: Docker Networking Configuration (.env file)

**Issue:** `POSTGRES_SERVER` and `REDIS_HOST` were set to `localhost`, which doesn't work inside Docker containers.

**Fix Applied:**
- Changed `POSTGRES_SERVER=localhost` → `POSTGRES_SERVER=postgres`
- Changed `REDIS_HOST=localhost` → `REDIS_HOST=redis`

**Files Modified:** `/backend/.env`

---

### 2. ✅ FIXED: SQLAlchemy Reserved Keyword - `metadata` Field

**Issue:** Two models used `metadata` as a column name, which is reserved by SQLAlchemy's Declarative API.

**Error Message:**
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

**Fix Applied:**
- Renamed `metadata` → `extra_data` in both models
- Updated `to_dict()` methods accordingly

**Files Modified:**
- `/backend/app/models/activity_log.py` (line 65, 114)
- `/backend/app/models/itinerary_activity_log.py` (line 55)

---

### 3. ❌ UNRESOLVED: Pydantic Circular Reference Recursion

**Issue:** `RecursionError: maximum recursion depth exceeded` during Pydantic schema initialization.

**Root Cause:** Circular forward references in schemas with complex nested relationships.

**What Causes It:**
- `ItineraryWithDetails` references `ItineraryDayWithDetails`
- `ItineraryDayWithDetails` references `DestinationResponse`, `AccommodationResponse` (as forward refs with strings)
- When Pydantic tries to resolve these during import, it creates an infinite loop

**Attempted Fixes:**
1. ✅ Removed `ItineraryWithDetails`, `ItineraryDayWithDetails`, `ItineraryPublicView` from `schemas/__init__.py` exports
2. ✅ Commented out `model_rebuild()` calls in `itinerary.py` and `base_tour.py`
3. ❌ Still failing - recursion happens during initial Pydantic type resolution

**Files Modified:**
- `/backend/app/schemas/__init__.py` (lines 119-141)
- `/backend/app/schemas/itinerary.py` (lines 580-582 commented)
- `/backend/app/schemas/base_tour.py` (lines 429-430 commented)

**Current Status:** ❌ Backend container fails to start

---

##  Recommended Solutions for Recursion Issue

### Option 1: Use `from __future__ import annotations` (RECOMMENDED)

Add this at the top of all schema files with forward references:

```python
from __future__ import annotations
```

This defers evaluation of type annotations until needed, preventing circular import issues.

**Files to modify:**
- `/backend/app/schemas/itinerary.py`
- `/backend/app/schemas/base_tour.py`
- `/backend/app/schemas/destination.py`
- `/backend/app/schemas/accommodation.py`
- `/backend/app/schemas/user.py`

---

### Option 2: Use `typing.TYPE_CHECKING`

Separate runtime imports from type-checking imports:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.destination import DestinationResponse
    from app.schemas.accommodation import AccommodationResponse
```

---

### Option 3: Remove Complex "WithDetails" Schemas (QUICK FIX)

Temporarily comment out the complex schemas and use simpler response models:

- Comment out `ItineraryWithDetails` class definition
- Comment out `ItineraryDayWithDetails` class definition
- Comment out `ItineraryPublicView` class definition
- Update endpoints to use `ItineraryResponse` instead

This gets the app running, but loses nested detail functionality.

---

## Environment Variable Warnings

These warnings appear during Docker operations but are **NOT CRITICAL**:

```
The "SECRET_KEY" variable is not set. Defaulting to a blank string.
The "SENDGRID_API_KEY" variable is not set. Defaulting to a blank string.
The "AZURE_STORAGE_CONNECTION_STRING" variable is not set. Defaulting to a blank string.
```

**Why:** Docker Compose tries to read these from the host environment before using values from `.env` file.

**Impact:** None - values are correctly loaded from `/backend/.env` inside containers.

**Optional Fix:** Export these in your shell if you want to eliminate warnings:
```bash
export SECRET_KEY=""
export SENDGRID_API_KEY=""
export AZURE_STORAGE_CONNECTION_STRING=""
export AZURE_STORAGE_CONTAINER=""
```

---

## Current Docker Services Status

- ✅ **PostgreSQL**: Running and healthy
- ✅ **Redis**: Running and healthy
- ❌ **Backend (FastAPI)**: Failing to start due to Pydantic recursion error

---

## Next Steps

1. **Implement Option 1** (recommended) - Add `from __future__ import annotations` to all schema files
2. **Test import** - Run `python -c "from app.main import app"` inside container to verify
3. **Run migrations** - `docker-compose exec backend alembic upgrade head`
4. **Seed database** - `docker-compose exec backend python seed_data.py`
5. **Test endpoints** - `curl http://localhost:8000/health`

---

## Files Successfully Fixed

1. `/backend/.env` - Docker networking configuration
2. `/backend/app/models/activity_log.py` - Renamed metadata field
3. `/backend/app/models/itinerary_activity_log.py` - Renamed metadata field
4. `/backend/app/schemas/__init__.py` - Removed problematic exports (partial fix)

---

## Test Report Reference

See `/backend/TEST_REPORT.md` for comprehensive production readiness audit results. All application logic bugs were fixed - only deployment/schema initialization issues remain.
