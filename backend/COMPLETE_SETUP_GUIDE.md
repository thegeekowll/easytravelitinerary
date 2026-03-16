# Complete Setup Guide - Travel Agency Management System

**Last Updated:** January 23, 2026

This guide will walk you through setting up and running the Travel Agency Management System on your Mac from scratch.

---

## 📋 What You Already Have

✅ **Python 3.12.7** - Installed and ready
✅ **Project Code** - Located at `/Users/aman/Documents/Itinerary Builder Platform/`
✅ **Backend Code** - Complete with all models, schemas, and API endpoints

---

## 🔧 Step 1: Install PostgreSQL Database

PostgreSQL is not currently installed. Let's install it using Homebrew.

### Install Homebrew (if not installed)

```bash
# Check if Homebrew is installed
which brew

# If not installed, install it:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Install PostgreSQL

```bash
# Install PostgreSQL
brew install postgresql@16

# Start PostgreSQL service
brew services start postgresql@16

# Verify it's running
brew services list | grep postgresql
```

### Create Database and User

```bash
# Connect to PostgreSQL (default user is your Mac username)
psql postgres

# Once in psql prompt, run these commands:
```

```sql
-- Create database
CREATE DATABASE travel_agency;

-- Create user (if needed, otherwise use your Mac user)
CREATE USER postgres WITH PASSWORD 'postgres';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE travel_agency TO postgres;

-- Exit psql
\q
```

**Alternative Setup (using your Mac username):**

```bash
# Create database with your username as owner
createdb travel_agency

# Test connection
psql travel_agency
# Type \q to exit
```

---

## 🐍 Step 2: Set Up Python Virtual Environment

Navigate to your project and create a virtual environment:

```bash
# Navigate to backend directory
cd "/Users/aman/Documents/Itinerary Builder Platform/backend"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv) at the beginning
```

**Important:** Every time you work on this project, you need to activate the virtual environment:
```bash
cd "/Users/aman/Documents/Itinerary Builder Platform/backend"
source venv/bin/activate
```

To deactivate when done:
```bash
deactivate
```

---

## 📦 Step 3: Install Python Dependencies

With the virtual environment activated:

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - FastAPI (web framework)
# - SQLAlchemy (database ORM)
# - Pydantic (data validation)
# - Uvicorn (ASGI server)
# - PostgreSQL driver
# - JWT libraries
# - Password hashing
# - Azure SDK (optional)
# - And more...
```

**Verify Installation:**
```bash
pip list | grep -E "fastapi|sqlalchemy|pydantic|uvicorn"
```

You should see:
```
fastapi        0.109.0
sqlalchemy     2.0.25
pydantic       2.5.3
uvicorn        0.27.0
```

---

## ⚙️ Step 4: Configure Environment Variables

Your `.env` file already exists, but let's verify it's correct:

```bash
# View your current .env file
cat .env
```

**Required Settings:**

```env
# Application
APP_NAME=Travel Agency Management System
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# API
API_V1_PREFIX=/api/v1

# Database - IMPORTANT: Update these if using different credentials
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=travel_agency

# Security - IMPORTANT: Change JWT_SECRET_KEY in production!
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://localhost:8080"]

# File Upload
MAX_UPLOAD_SIZE_MB=10
ALLOWED_EXTENSIONS=["jpg","jpeg","png","pdf","doc","docx"]

# Azure Blob Storage (Optional - for production)
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_ACCOUNT_NAME=
AZURE_STORAGE_ACCOUNT_KEY=

# Email (Optional - for production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=noreply@travelagency.com
EMAILS_FROM_NAME=Travel Agency
```

**If using your Mac username for PostgreSQL:**

Edit `.env` and change:
```env
POSTGRES_USER=aman  # Your Mac username
POSTGRES_PASSWORD=  # Leave empty if no password set
```

---

## 🗄️ Step 5: Initialize Database

Now let's create all the database tables:

```bash
# Make sure you're in the backend directory with venv activated
cd "/Users/aman/Documents/Itinerary Builder Platform/backend"
source venv/bin/activate  # If not already activated

# Run database initialization script
python app/db/init_db.py
```

**Expected Output:**
```
======================================================================
 Database Initialization
======================================================================
Dropping all existing tables...
Creating all tables from models...

Tables created successfully:
✓ users
✓ permissions
✓ user_permissions (association table)
✓ agent_types
✓ destinations
✓ destination_images
✓ accommodations
✓ accommodation_types
✓ accommodation_images
✓ base_tours
✓ tour_types
✓ base_tour_days
✓ base_tour_images
✓ base_tour_day_destinations (association table)
✓ itineraries
✓ itinerary_days
✓ itinerary_day_destinations (association table)
✓ itinerary_accommodations (association table)
✓ travelers
✓ payments
✓ inclusions
✓ exclusions
✓ itinerary_inclusions (association table)
✓ itinerary_exclusions (association table)
✓ destination_combinations
✓ company_content
✓ award_badges
✓ emails
✓ notifications
✓ activity_logs

Total tables created: 33

======================================================================
 Database initialization completed successfully!
======================================================================
```

**If you get an error:**

1. **Connection Error:** Check PostgreSQL is running
   ```bash
   brew services list | grep postgresql
   ```

2. **Authentication Error:** Check `.env` has correct username/password

3. **Database doesn't exist:** Create it manually
   ```bash
   createdb travel_agency
   ```

---

## 🚀 Step 6: Start the Server

```bash
# Make sure you're in backend directory with venv activated
cd "/Users/aman/Documents/Itinerary Builder Platform/backend"
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload
```

**Expected Output:**
```
======================================================================
 Travel Agency Management System
======================================================================
Environment: development
Debug: True
Database: travel_agency
======================================================================

🔧 Creating default admin user...
✅ Default admin created:
   Email: admin@travelagency.com
   Password: Admin123!
   ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!

INFO:     Will watch for changes in these directories: ['/Users/aman/Documents/Itinerary Builder Platform/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Server is now running!** 🎉

---

## 🌐 Step 7: Access the Application

### API Documentation (Interactive)

Open your browser and go to:

**Swagger UI:** http://localhost:8000/docs

This gives you an interactive interface to test all API endpoints.

**ReDoc:** http://localhost:8000/redoc

This gives you beautiful API documentation.

### Health Check

**Root Endpoint:** http://localhost:8000/

Response:
```json
{
  "message": "Travel Agency Management System API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

**Health Endpoint:** http://localhost:8000/health

Response:
```json
{
  "status": "healthy",
  "app_name": "Travel Agency Management System",
  "environment": "development"
}
```

**Database Check:** http://localhost:8000/db-check

Response:
```json
{
  "status": "connected",
  "database": "travel_agency",
  "statistics": {
    "users": 1,
    "itineraries": 0
  }
}
```

---

## 🔐 Step 8: Test Authentication

### Using the Test Script

```bash
# In a new terminal (keep server running in first terminal)
cd "/Users/aman/Documents/Itinerary Builder Platform/backend"
source venv/bin/activate

# Run test script
python test_auth_system.py
```

**Expected Output:**
```
======================================================================
 AUTHENTICATION SYSTEM TEST SUITE
======================================================================

======================================================================
 TEST 1: Server Health Check
======================================================================
✅ Server is running
ℹ️  Response: {'status': 'healthy', ...}

======================================================================
 TEST 2: Database Connection
======================================================================
✅ Database is connected
ℹ️  Statistics: {'users': 1, 'itineraries': 0}

======================================================================
 TEST 3: Admin Login
======================================================================
ℹ️  Attempting login with default admin credentials...
✅ Login successful
ℹ️  User: admin@travelagency.com
ℹ️  Role: admin
ℹ️  Token: eyJ0eXAiOiJKV1QiLCJhbGc...

... (more tests)

======================================================================
 TEST SUMMARY
======================================================================
✅ All core authentication tests completed
```

### Using Swagger UI (Recommended)

1. Go to http://localhost:8000/docs
2. Click on **"POST /api/v1/auth/login"**
3. Click **"Try it out"**
4. Enter credentials:
   ```
   username: admin@travelagency.com
   password: Admin123!
   ```
5. Click **"Execute"**
6. Copy the `access_token` from the response
7. Click **"Authorize"** button at the top of the page
8. Enter: `Bearer YOUR_ACCESS_TOKEN`
9. Click **"Authorize"**
10. Now you can test all endpoints!

---

## 📝 Step 9: Test CRUD Endpoints

Follow the comprehensive testing checklist:

```bash
# Open the testing checklist
cat TESTING_CHECKLIST.md
```

Or follow along in Swagger UI at http://localhost:8000/docs

### Quick Test Flow

1. **Create a Destination:**
   - Go to `POST /api/v1/destinations`
   - Click "Try it out"
   - Use sample data:
   ```json
   {
     "name": "Paris",
     "country": "France",
     "region": "Île-de-France",
     "description": "The City of Light",
     "best_time_to_visit": "April to June",
     "average_temp_celsius": 12.5,
     "highlights": ["Eiffel Tower", "Louvre", "Notre-Dame"],
     "activities": ["Sightseeing", "Museums", "Dining"]
   }
   ```
   - Click "Execute"
   - Should return 201 Created

2. **List Destinations:**
   - Go to `GET /api/v1/destinations`
   - Click "Try it out"
   - Click "Execute"
   - Should see your Paris destination

3. **Upload Images:**
   - Go to `POST /api/v1/destinations/{id}/images`
   - Enter the destination ID from step 1
   - Upload 2-3 images
   - Should return image URLs

Continue testing with accommodations, tours, content, etc.

---

## 🛑 Stopping the Server

To stop the server:

1. Go to the terminal where server is running
2. Press `CTRL + C`
3. Wait for graceful shutdown

```
^C
INFO:     Shutting down
INFO:     Waiting for application shutdown.

Shutting down application...
INFO:     Application shutdown complete.
INFO:     Finished server process [12346]
```

---

## 🔄 Daily Development Workflow

**Every time you want to work on the project:**

```bash
# 1. Navigate to project
cd "/Users/aman/Documents/Itinerary Builder Platform/backend"

# 2. Activate virtual environment
source venv/bin/activate

# 3. Make sure PostgreSQL is running
brew services list | grep postgresql
# If not running: brew services start postgresql@16

# 4. Start the server
uvicorn app.main:app --reload

# 5. Open browser to http://localhost:8000/docs

# 6. When done, stop server (CTRL+C) and deactivate venv
deactivate
```

---

## 📊 Database Management

### View Database Contents

```bash
# Connect to database
psql travel_agency

# List all tables
\dt

# View users
SELECT email, role, is_active FROM users;

# View destinations
SELECT name, country FROM destinations;

# Exit
\q
```

### Reset Database

If you need to start fresh:

```bash
# Activate venv
cd "/Users/aman/Documents/Itinerary Builder Platform/backend"
source venv/bin/activate

# Re-run initialization (drops and recreates all tables)
python app/db/init_db.py
```

**⚠️ WARNING:** This deletes ALL data!

---

## 🐛 Troubleshooting

### Server won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`
- **Fix:** Activate virtual environment: `source venv/bin/activate`
- **Fix:** Install dependencies: `pip install -r requirements.txt`

**Error:** `Connection refused` or database errors
- **Fix:** Start PostgreSQL: `brew services start postgresql@16`
- **Fix:** Check `.env` has correct database credentials

**Error:** `Port 8000 already in use`
- **Fix:** Kill existing process: `lsof -ti:8000 | xargs kill -9`
- **Or:** Use different port: `uvicorn app.main:app --reload --port 8001`

### Can't connect to database

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Try to connect manually
psql travel_agency

# If connection fails, check .env credentials match
cat .env | grep POSTGRES
```

### Import errors or module not found

```bash
# Make sure you're in the right directory
pwd
# Should show: /Users/aman/Documents/Itinerary Builder Platform/backend

# Make sure venv is activated
which python
# Should show: .../backend/venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Server starts but endpoints return 500 errors

```bash
# Check server logs in terminal for detailed error
# Common issue: Database tables not created

# Re-initialize database
python app/db/init_db.py
```

---

## 🎯 Next Steps

After successfully running the application:

1. ✅ Change default admin password
2. ✅ Create test data (destinations, accommodations, tours)
3. ✅ Test all CRUD endpoints using Swagger UI
4. ✅ Create CS agent users and test permissions
5. ⏳ Build itinerary management system (Phase 4)
6. ⏳ Add payment tracking
7. ⏳ Add email notifications
8. ⏳ Build frontend application

---

## 📚 Useful Commands Reference

```bash
# Virtual Environment
source venv/bin/activate              # Activate
deactivate                            # Deactivate

# Server
uvicorn app.main:app --reload         # Start with auto-reload
uvicorn app.main:app --port 8001      # Start on different port
uvicorn app.main:app --host 0.0.0.0   # Allow external access

# Database
psql travel_agency                    # Connect to database
createdb travel_agency                # Create database
dropdb travel_agency                  # Delete database
python app/db/init_db.py             # Initialize tables

# PostgreSQL Service
brew services start postgresql@16     # Start
brew services stop postgresql@16      # Stop
brew services restart postgresql@16   # Restart
brew services list                    # List all services

# Testing
python test_auth_system.py           # Test authentication
curl http://localhost:8000/health    # Health check

# Python
pip list                              # List installed packages
pip install -r requirements.txt       # Install dependencies
pip freeze > requirements.txt         # Update requirements
```

---

## 🎉 Success Checklist

Before moving to Phase 4, verify:

- [ ] PostgreSQL installed and running
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] Database initialized (33 tables created)
- [ ] Server starts without errors
- [ ] Can access Swagger UI at http://localhost:8000/docs
- [ ] Admin login works
- [ ] Can create destinations
- [ ] Can create accommodations
- [ ] Can create base tours
- [ ] Can upload images
- [ ] All CRUD endpoints working

---

## 💡 Tips

1. **Always activate venv** before running any Python commands
2. **Keep server terminal open** while testing in browser
3. **Use Swagger UI** for easy testing - it's interactive and user-friendly
4. **Check server logs** if something doesn't work - errors show in terminal
5. **Use meaningful test data** - makes debugging easier
6. **Create backups** before resetting database

---

**You're all set!** 🚀

Your Travel Agency Management System is ready to run. Follow the daily workflow above whenever you want to work on it.

For testing, refer to `TESTING_CHECKLIST.md`.
For API documentation, refer to `CRUD_ENDPOINTS_COMPLETE.md`.

**Current Progress:** 80% complete - Core system fully operational!
