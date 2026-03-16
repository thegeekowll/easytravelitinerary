# Database Setup & Testing Guide

Complete step-by-step guide to set up and test your Travel Agency Management System database.

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start PostgreSQL (if not running)
# Method 1: Docker
docker run --name postgres-travel -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16

# Method 2: Local PostgreSQL
# brew services start postgresql (macOS)
# sudo systemctl start postgresql (Linux)

# 4. Create database
createdb travel_agency

# 5. Initialize database
python app/db/init_db.py

# 6. Run tests
python test_models.py

# 7. Start application
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

---

## 📋 Detailed Setup Instructions

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.109.0 sqlalchemy-2.0.25 ...
```

**Common errors:**
- `pip: command not found` → Install Python 3.11+
- `error: Microsoft Visual C++ required` → Install build tools (Windows)

---

### Step 2: Configure Environment

The `.env` file has been created with development defaults.

**Review settings:**
```bash
cat .env
```

**Key settings to verify:**
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=travel_agency
POSTGRES_PORT=5432
```

**Customize if needed:**
```bash
nano .env  # or vim, code, etc.
```

---

### Step 3: Start PostgreSQL

Choose one method:

#### Option A: Docker (Recommended)
```bash
# Start PostgreSQL container
docker run --name postgres-travel \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:16

# Verify it's running
docker ps
```

#### Option B: Local PostgreSQL
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Windows
# Start PostgreSQL service from Services panel
```

#### Verify PostgreSQL is running:
```bash
psql -U postgres -c "SELECT version();"
```

**Expected output:**
```
 PostgreSQL 16.x on ...
```

---

### Step 4: Create Database

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE travel_agency;"

# Or using createdb
createdb -U postgres travel_agency

# Verify
psql -U postgres -l | grep travel_agency
```

**Expected output:**
```
 travel_agency | postgres | UTF8 | ...
```

---

### Step 5: Verify Setup

```bash
python verify_setup.py
```

**Expected output:**
```
======================================================================
 SETUP VERIFICATION
======================================================================

======================================================================
 VERIFYING IMPORTS
======================================================================
📦 Importing core modules...
  ✅ app.core.config
  ✅ app.db.session
  ✅ app.core.security

📦 Importing models...
  ✅ All models imported successfully

✅ All imports successful

======================================================================
 VERIFYING DATABASE CONNECTION
======================================================================

📊 Database: travel_agency
🖥️  Server: localhost:5432
👤 User: postgres

✅ Connected to PostgreSQL
   Version: PostgreSQL 16.1

======================================================================
 VERIFYING TABLES
======================================================================

⚠️  Missing 33 tables:
   - accommodations
   - activity_logs
   ...

======================================================================
 VERIFYING CONFIGURATION
======================================================================

✓ Required Configuration:
  ✅ Database URL
  ✅ Secret Key
  ✅ JWT Secret
  ✅ CORS Origins

ℹ️  Optional Configuration:
  ⚠️  Not set SendGrid API Key
  ⚠️  Not set Azure Storage

======================================================================
 SUMMARY
======================================================================
  ✅ PASS: Imports
  ✅ PASS: Database Connection
  ❌ FAIL: Tables
  ✅ PASS: Configuration
```

**Note:** Tables check will fail initially - this is expected!

---

### Step 6: Initialize Database

```bash
python app/db/init_db.py
```

**Expected output:**
```
======================================================================
 DATABASE INITIALIZATION
======================================================================

📊 Database: travel_agency
🖥️  Server: localhost:5432
👤 User: postgres

🔌 Testing database connection...
✅ Database connection successful

🏗️  Creating database tables...
✅ Table creation complete

🔍 Verifying tables...

📋 Found 33 tables:
----------------------------------------------------------------------
  ✅ accommodations
  ✅ accommodation_images
  ✅ accommodation_types
  ✅ activity_logs
  ✅ agent_types
  ✅ base_tour_day_destinations
  ✅ base_tour_days
  ✅ base_tour_exclusions
  ✅ base_tour_images
  ✅ base_tour_inclusions
  ✅ base_tours
  ✅ company_assets
  ✅ company_content
  ✅ destination_combinations
  ✅ destination_images
  ✅ destinations
  ✅ email_logs
  ✅ exclusions
  ✅ inclusions
  ✅ itineraries
  ✅ itinerary_activity_logs
  ✅ itinerary_day_destinations
  ✅ itinerary_days
  ✅ itinerary_exclusions
  ✅ itinerary_featured_accommodations
  ✅ itinerary_inclusions
  ✅ notifications
  ✅ payment_records
  ✅ permissions
  ✅ tour_types
  ✅ travelers
  ✅ user_permissions
  ✅ users
----------------------------------------------------------------------

======================================================================
✅ DATABASE INITIALIZATION SUCCESSFUL
======================================================================

Total tables: 33
Expected tables: 33
All required tables: ✅ Present
```

---

### Step 7: Run Model Tests

```bash
python test_models.py
```

**Expected output (abbreviated):**
```
======================================================================
 STARTING DATABASE MODEL TESTS
======================================================================

======================================================================
 TEST 1: User & Permission Models
======================================================================
✅ Created admin user: admin@test.com
✅ Created CS agent: agent@test.com
✅ Created permission: create_itinerary
✅ Assigned permission to agent

======================================================================
 TEST 2: Agent Type Model
======================================================================
✅ Created agent type: Safari Specialist

======================================================================
 TEST 3: Destination Models
======================================================================
✅ Created destination: Serengeti National Park
✅ Created destination: Ngorongoro Crater
✅ Created destination image

======================================================================
 TEST 4: Destination Combination (2D Table)
======================================================================
✅ Created destination combination: Serengeti National Park, Ngorongoro Crater
✅ Lookup test passed: Found combination

======================================================================
 TEST 5: Accommodation Models
======================================================================
✅ Created accommodation type: Luxury Tented Camp
✅ Created accommodation: Serengeti Safari Camp

======================================================================
 TEST 6: Base Tour Models
======================================================================
✅ Created tour type: Small Group Safari
✅ Created inclusion: Accommodation
✅ Created exclusion: International Flights
✅ Created base tour: 5-Day Serengeti Safari
✅ Created base tour day: Day 1

======================================================================
 TEST 7: Itinerary Models
======================================================================
✅ Created itinerary: ABC123XYZ456
   Public URL: https://example.com/itinerary/ABC123XYZ456
✅ Created traveler: John Doe
✅ Created itinerary day: Day 1
   Auto-filled: True

======================================================================
 TEST 8: Payment, Email, Notification Models
======================================================================
✅ Created payment record: partially_paid
✅ Created email log: Your Safari Itinerary
✅ Created activity log: created
✅ Created notification: New Itinerary Assigned

======================================================================
 TEST 9: Company Models
======================================================================
✅ Created company content: intro_letter_template
✅ Created company asset: Company Logo

======================================================================
 TEST 10: Relationship Tests
======================================================================
User CS Agent:
  Created itineraries: 0
  Assigned itineraries: 1

Itinerary ABC123XYZ456:
  Days: 1
  Travelers: 1
  Primary traveler: John Doe

Base Tour 5-Day Serengeti Safari:
  Days: 1
  Inclusions: 1
  Exclusions: 1

Destination Serengeti National Park:
  Images: 1

✅ All relationship tests passed

======================================================================
 TEST 11: Method Tests
======================================================================
Itinerary.is_editable('cs_agent'): True
Itinerary.is_tour_ended: False
Itinerary.get_public_url(): https://example.com/itinerary/ABC123XYZ456

User.verify_password('Admin123!'): True
Agent.has_permission(CREATE_ITINERARY): True
Admin.is_admin: True

✅ All method tests passed

======================================================================
 COMMITTING CHANGES
======================================================================
✅ All changes committed to database

======================================================================
 VERIFICATION
======================================================================
  Users: 2
  Permissions: 1
  Destinations: 2
  Accommodations: 1
  Base Tours: 1
  Itineraries: 1
  Travelers: 1
  Destination Combinations: 1
  Notifications: 1

======================================================================
 ALL TESTS COMPLETED SUCCESSFULLY ✅
======================================================================
```

**To clean up test data:**
```bash
python test_models.py --cleanup
```

---

### Step 8: Start Application

```bash
uvicorn app.main:app --reload
```

**Expected output:**
```
======================================================================
 Travel Agency Management System
======================================================================
Environment: development
Debug: True
Database: travel_agency
======================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 9: Test API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "app_name": "Travel Agency Management System",
  "environment": "development"
}
```

#### Database Check
```bash
curl http://localhost:8000/db-check
```

**Expected response:**
```json
{
  "status": "connected",
  "database": "travel_agency",
  "statistics": {
    "users": 2,
    "itineraries": 1
  }
}
```

#### API Documentation
Visit: http://localhost:8000/docs

You should see the interactive Swagger UI.

---

## 🔧 Using Alembic Migrations

### Create Initial Migration

```bash
alembic revision --autogenerate -m "Initial migration"
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added table 'permissions'
...
  Generating /path/to/alembic/versions/2026_01_23_1234-abc123_initial_migration.py ...  done
```

### Apply Migration

```bash
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial migration
```

### Check Migration Status

```bash
alembic current
```

### Rollback Migration

```bash
alembic downgrade -1
```

---

## ❌ Common Errors & Solutions

### Error 1: "No module named 'app'"

**Error:**
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

### Error 2: "connection refused"

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server: Connection refused
```

**Solutions:**
1. Check PostgreSQL is running:
   ```bash
   psql -U postgres -c "SELECT 1;"
   ```

2. Check port 5432:
   ```bash
   netstat -an | grep 5432
   # or
   lsof -i :5432
   ```

3. Verify credentials in `.env`

---

### Error 3: "database does not exist"

**Error:**
```
sqlalchemy.exc.OperationalError: FATAL: database "travel_agency" does not exist
```

**Solution:**
```bash
createdb -U postgres travel_agency
```

---

### Error 4: "password authentication failed"

**Error:**
```
sqlalchemy.exc.OperationalError: FATAL: password authentication failed for user "postgres"
```

**Solution:**
Update `.env` file with correct password:
```env
POSTGRES_PASSWORD=your_actual_password
```

---

### Error 5: "relation already exists"

**Error:**
```
sqlalchemy.exc.ProgrammingError: relation "users" already exists
```

**Solution:**
Tables already exist. Either:
1. Drop all tables first:
   ```bash
   python app/db/init_db.py --drop
   ```
2. Or use Alembic migrations instead

---

### Error 6: Import errors in models

**Error:**
```
ImportError: cannot import name 'BaseTour' from 'app.models'
```

**Solution:**
1. Check `/backend/app/models/__init__.py` has proper exports
2. Check for circular imports
3. Restart Python interpreter

---

## 🗄️ Database Management

### Connect to Database

```bash
psql -U postgres -d travel_agency
```

### Useful SQL Commands

```sql
-- List all tables
\dt

-- Describe table structure
\d users

-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM itineraries;

-- View recent itineraries
SELECT unique_code, tour_title, status, created_at 
FROM itineraries 
ORDER BY created_at DESC 
LIMIT 10;

-- Check relationships
SELECT u.full_name, COUNT(i.id) as itinerary_count
FROM users u
LEFT JOIN itineraries i ON i.assigned_to_user_id = u.id
GROUP BY u.id, u.full_name;
```

### Backup Database

```bash
pg_dump -U postgres travel_agency > backup.sql
```

### Restore Database

```bash
psql -U postgres travel_agency < backup.sql
```

---

## ✅ Verification Checklist

- [ ] PostgreSQL is running
- [ ] Database `travel_agency` exists
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] `python verify_setup.py` passes all checks
- [ ] `python app/db/init_db.py` creates all tables
- [ ] `python test_models.py` passes all tests
- [ ] `uvicorn app.main:app --reload` starts successfully
- [ ] http://localhost:8000/health returns healthy status
- [ ] http://localhost:8000/docs shows API documentation

---

## 📚 Next Steps

After successful setup:

1. **Create Admin User:**
   ```python
   from app.db.session import SessionLocal
   from app.models import User
   from app.core.security import get_password_hash

   db = SessionLocal()
   admin = User(
       email="admin@youragency.com",
       hashed_password=get_password_hash("YourPassword123!"),
       full_name="System Admin",
       role="admin",
       is_active=True
   )
   db.add(admin)
   db.commit()
   ```

2. **Seed Initial Data:**
   - Create destinations
   - Create accommodation types
   - Create tour types
   - Create destination combinations

3. **Develop API Endpoints:**
   - Authentication endpoints
   - Itinerary CRUD
   - User management
   - etc.

4. **Frontend Integration:**
   - Connect Next.js frontend
   - Test authentication flow
   - Build itinerary builder UI

---

## 🆘 Getting Help

If you encounter issues:

1. Check logs in `logs/app.log`
2. Run verification: `python verify_setup.py`
3. Check database connection: `psql -U postgres -d travel_agency`
4. Review error messages carefully
5. Check this guide's "Common Errors" section

---

**Setup Time:** ~10-15 minutes
**Status:** Ready for development! 🚀
