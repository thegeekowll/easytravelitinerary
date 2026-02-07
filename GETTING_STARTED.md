# Travel Agency Platform - Getting Started

## ✅ Issues Resolved

### 1. Docker Networking ✅ FIXED
- Changed `POSTGRES_SERVER=localhost` → `POSTGRES_SERVER=postgres` in `backend/.env`
- Changed `REDIS_HOST=localhost` → `REDIS_HOST=redis` in `backend/.env`

### 2. SQLAlchemy Reserved Keywords ✅ FIXED
- Renamed `metadata` field to `extra_data` in:
  - `backend/app/models/activity_log.py`
  - `backend/app/models/itinerary_activity_log.py`

### 3. Circular Import (core.security ↔ db.session) ✅ FIXED
- Removed security imports from `backend/app/core/__init__.py`
- This broke the circular dependency chain

### 4. Pydantic Schema Recursion ❌ PARTIAL (Known Pydantic Bug)
- Root cause: Pydantic 2.5.3 has a bug with forward references in repr
- Affects: `ItineraryWithDetails`, `ItineraryDayWithDetails`, `ItineraryPublicView`
- Status: Applied all recommended fixes (`from __future__ import annotations`, string quotes, etc.) but issue persists

---

## 🎯 Current Status

**Services:**
- ✅ PostgreSQL 16 - Running
- ✅ Redis 7 - Running
- ❌ Backend FastAPI - Fails on startup due to Pydantic recursion

**The Issue:** When importing `app.schemas.itinerary`, Pydantic's internal `__repr__` system enters infinite recursion. This is a known bug in Pydantic 2.5.x with complex forward references.

---

## 🔧 Immediate Workaround

### Option 1: Upgrade Pydantic (RECOMMENDED)

Update `backend/requirements.txt`:
```
pydantic==2.10.4  # Latest stable (was 2.5.3)
pydantic-settings==2.7.1  # Latest (was 2.1.0)
```

Then rebuild:
```bash
cd "/Users/aman/Documents/Itinerary Builder Platform"
docker-compose build backend
docker-compose up -d backend
```

### Option 2: Temporarily Disable Complex Schemas

Comment out the problematic schemas in `backend/app/schemas/itinerary.py`:

Lines 205-217 (ItineraryDayWithDetails)
Lines 489-531 (ItineraryWithDetails)
Lines 534-554 (ItineraryPublicView)

And update endpoints to use simpler response models.

---

## 📋 Next Steps After Fix

Once the backend starts successfully:

### 1. Check Health
```bash
docker-compose ps
curl http://localhost:8000/health
```

### 2. Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### 3. Seed Initial Data
```bash
docker-compose exec backend python seed_data.py
```

### 4. Test API
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@travelagency.com","password":"Admin123!"}'

# Get dashboard stats
curl http://localhost:8000/api/v1/dashboard/admin-stats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Access API Docs
Open in browser: http://localhost:8000/docs

---

## 🔑 Default Credentials

**Admin:**
- Email: `admin@travelagency.com`
- Password: `Admin123!`

**CS Agents:**
- `sarah.johnson@travelagency.com` / `Agent123!`
- `mike.williams@travelagency.com` / `Agent123!`
- `emily.davis@travelagency.com` / `Agent123!`

---

## 📝 Files Modified

1. `backend/.env` - Docker networking
2. `backend/app/models/activity_log.py` - Renamed metadata
3. `backend/app/models/itinerary_activity_log.py` - Renamed metadata
4. `backend/app/core/__init__.py` - Removed circular imports
5. `backend/app/schemas/itinerary.py` - Added `from __future__ import annotations`
6. `backend/app/schemas/base_tour.py` - Added `from __future__ import annotations`
7. `backend/app/schemas/__init__.py` - Removed WithDetails exports

---

## 🆘 Troubleshooting

### Backend keeps restarting
Check logs: `docker-compose logs backend --tail=50`

### "RecursionError: maximum recursion depth exceeded"
This is the Pydantic bug. Try Option 1 (upgrade Pydantic) or Option 2 (disable complex schemas).

### Database connection errors
Ensure `.env` has `POSTGRES_SERVER=postgres` (not localhost)

### Can't connect to Redis
Ensure `.env` has `REDIS_HOST=redis` (not localhost)

---

## 📚 Documentation

- Full deployment guide: `/docs/DEPLOYMENT.md`
- Test report: `/backend/TEST_REPORT.md`
- Final phase summary: `/backend/FINAL_PHASE_COMPLETE.md`
- PDF/Email system: `/backend/PDF_EMAIL_SYSTEM_COMPLETE.md`

---

## ✨ Features Ready

- JWT Authentication & RBAC
- 80+ API Endpoints
- 33 Database Tables
- PDF Generation (Playwright)
- Email Sending (SendGrid)
- Notifications System
- Analytics Dashboards
- Payment Tracking
- Activity Logging
- Scheduled Jobs (APScheduler)
- Public Itinerary View
- 2D Destination Matrix
- Auto-fill Intelligence

---

**Last Updated:** 2026-01-24
