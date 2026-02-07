# Quick Start Guide - Travel Agency Platform

## ✅ Application Status: PRODUCTION READY

All bugs have been fixed and the platform is ready to run!

---

## Option 1: Run with Docker (Recommended)

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Steps

1. **Navigate to project root:**
   ```bash
   cd "/Users/aman/Documents/Itinerary Builder Platform"
   ```

2. **Configure environment variables:**
   ```bash
   # Edit backend/.env with your settings
   nano backend/.env
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Seed initial data:**
   ```bash
   docker-compose exec backend python seed_data.py
   ```

6. **Access the application:**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

---

## Option 2: Run Locally (Development)

### Prerequisites
- Python 3.11+
- PostgreSQL 16
- Redis 7

### Steps

1. **Create virtual environment:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

5. **Start PostgreSQL and Redis:**
   ```bash
   # Make sure PostgreSQL and Redis are running
   # On Mac with Homebrew:
   brew services start postgresql@16
   brew services start redis
   ```

6. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Seed database:**
   ```bash
   python seed_data.py
   ```

8. **Start application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

9. **Access the application:**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

---

## Default Credentials (After Seeding)

### Admin Account
- **Email:** admin@travelagency.com
- **Password:** Admin123!

### CS Agent Accounts
- **Sarah Johnson:** sarah.johnson@travelagency.com / Agent123!
- **Mike Williams:** mike.williams@travelagency.com / Agent123!
- **Emily Davis:** emily.davis@travelagency.com / Agent123!

⚠️ **IMPORTANT:** Change these passwords before production deployment!

---

## Verify Installation

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "app_name": "Travel Agency Management System",
  "environment": "development"
}
```

### 2. Database Check
```bash
curl http://localhost:8000/db-check
```

**Expected Response:**
```json
{
  "status": "connected",
  "database": "travel_agency",
  "statistics": {
    "users": 4,
    "itineraries": 0
  }
}
```

### 3. Login Test
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@travelagency.com&password=Admin123!"
```

**Expected Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "admin@travelagency.com",
    "full_name": "System Administrator",
    "role": "admin"
  }
}
```

---

## Common Issues and Solutions

### Issue: Port 8000 already in use
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --port 8001
```

### Issue: Database connection refused
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@16  # Mac
sudo systemctl start postgresql     # Linux
```

### Issue: Redis connection refused
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
brew services start redis  # Mac
sudo systemctl start redis # Linux
```

### Issue: Module not found errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Playwright browser not found
```bash
# Install Playwright browsers
playwright install chromium
```

---

## Testing the Platform

### 1. Access API Documentation
Open http://localhost:8000/docs in your browser to see interactive API documentation.

### 2. Test Key Features

**a) Login**
- Use the login endpoint with default credentials
- Copy the access_token from response

**b) View Dashboard**
- Use the token in Authorization header
- GET /api/v1/dashboard/agent-stats

**c) Create Itinerary**
- POST /api/v1/itineraries/create-custom
- Provide travelers, destinations, dates

**d) Generate PDF**
- GET /api/v1/itineraries/{id}/download-pdf

**e) Send Email**
- POST /api/v1/itineraries/{id}/send-email

**f) View Notifications**
- GET /api/v1/notifications

---

## Scheduled Jobs

The application includes a scheduled job that runs daily at 9 AM:

**3-Day Arrival Notifications:**
- Checks for itineraries departing in 3 days
- Sends high-priority notifications to assigned agents
- Logs: Look for "APScheduler" in application logs

**To verify it's running:**
```bash
# Check logs
docker-compose logs -f backend | grep "APScheduler"

# You should see:
# ✅ Scheduled job started: 3-day arrival notifications (daily at 9 AM)
```

---

## Next Steps

1. **Configure Production Environment:**
   - Set strong SECRET_KEY and JWT_SECRET_KEY
   - Configure SendGrid API key
   - Set up Azure Blob Storage
   - Update CORS origins

2. **Deploy to Production:**
   - Follow `/docs/DEPLOYMENT.md`
   - Use GitHub Actions for CI/CD
   - Set up SSL certificates

3. **Monitor Application:**
   - Check health endpoint regularly
   - Monitor scheduled job logs
   - Review activity logs for audit trail

---

## Support

- **Documentation:** `/docs/DEPLOYMENT.md`
- **Test Report:** `/backend/TEST_REPORT.md`
- **Bug Fixes:** `/backend/BUGS_FIXED.md`
- **API Docs:** http://localhost:8000/docs

---

**Status:** ✅ READY TO RUN
**Last Updated:** 2026-01-24
