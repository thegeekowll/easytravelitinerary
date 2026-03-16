# Quick Start Guide - Authentication System

## Prerequisites

1. **Python 3.12** installed
2. **PostgreSQL** installed and running
3. **pip** package manager

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Key packages:
- FastAPI
- SQLAlchemy
- Pydantic
- python-jose[cryptography] (for JWT)
- passlib[bcrypt] (for passwords)
- psycopg2-binary (PostgreSQL driver)

### 2. Setup PostgreSQL Database

```bash
# Start PostgreSQL (if not running)
# Mac with Homebrew:
brew services start postgresql@14

# Or manually:
pg_ctl -D /usr/local/var/postgres start

# Create database
createdb travel_agency

# Or using psql:
psql postgres
CREATE DATABASE travel_agency;
\q
```

### 3. Configure Environment

The `.env` file is already configured with:
- Database: `travel_agency`
- User: `postgres`
- Password: `postgres`
- Host: `localhost`
- Port: `5432`

If your PostgreSQL uses different credentials, update `/backend/.env`:
```bash
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=travel_agency
```

### 4. Initialize Database

```bash
python app/db/init_db.py
```

This will:
- Create all 33 database tables
- Verify table creation
- Show statistics

Expected output:
```
======================================================================
 DATABASE INITIALIZATION
======================================================================

📊 Database: travel_agency
🖥️  Server: localhost:5432
👤 User: postgres

✅ Database connection successful
✅ Table creation complete
✅ Found 33 tables

======================================================================
✅ DATABASE INITIALIZATION SUCCESSFUL
======================================================================
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload
```

The server will:
- Start on `http://localhost:8000`
- Create default admin user (if none exists)
- Enable auto-reload on code changes

Expected startup output:
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

INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Test the System

Open another terminal and run:

```bash
python test_auth_system.py
```

This will:
1. Check server health
2. Test database connection
3. Login with admin credentials
4. Retrieve admin profile
5. Create a test CS agent
6. List all users
7. Login with agent credentials

### 7. Explore API Documentation

Open your browser:

- **Swagger UI (Interactive):** http://localhost:8000/docs
- **ReDoc (Documentation):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **Database Check:** http://localhost:8000/db-check

---

## Quick Test with curl

### 1. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@travelagency.com&password=Admin123!"
```

Copy the `access_token` from the response.

### 2. Get Profile
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 3. Create New User
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newagent@example.com",
    "full_name": "New Agent",
    "password": "NewAgent123!",
    "role": "cs_agent"
  }'
```

---

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'jose'
**Solution:**
```bash
pip install python-jose[cryptography]
```

### Issue: ModuleNotFoundError: No module named 'passlib'
**Solution:**
```bash
pip install passlib[bcrypt]
```

### Issue: psycopg2 installation fails
**Solution:**
```bash
# Use binary version
pip install psycopg2-binary
```

### Issue: Database connection failed
**Solution:**
1. Check PostgreSQL is running:
   ```bash
   pg_isready
   ```

2. Check database exists:
   ```bash
   psql -l | grep travel_agency
   ```

3. Test connection manually:
   ```bash
   psql -U postgres -d travel_agency
   ```

### Issue: pydantic_settings parsing error
**Solution:**
Already fixed! The `.env` file now uses JSON format for list fields:
```bash
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
ALLOWED_EXTENSIONS=["jpg","jpeg","png","pdf","doc","docx"]
```

---

## Default Credentials

**Admin:**
- Email: `admin@travelagency.com`
- Password: `Admin123!`

⚠️ Change this password after first login!

---

## Available Endpoints

### Authentication (`/api/v1/auth`)
- `POST /login` - User login
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user profile
- `POST /logout` - Logout (client-side cleanup)

### User Management (`/api/v1/users`)
- `GET /users` - List all users (admin)
- `POST /users` - Create new user (admin)
- `GET /users/{id}` - Get user details
- `PATCH /users/{id}` - Update user
- `DELETE /users/{id}` - Delete/deactivate user (admin)
- `GET /users/{id}/permissions` - Get user permissions (admin)
- `PUT /users/{id}/permissions` - Set user permissions (admin)
- `POST /users/{id}/reactivate` - Reactivate user (admin)

---

## Next Steps

After successful setup:

1. **Change Admin Password**
   - Login to Swagger UI
   - Use PATCH `/api/v1/users/{id}` endpoint
   - Update password

2. **Create More Users**
   - Create CS agent accounts
   - Assign appropriate permissions

3. **Test Permission System**
   - Create permissions
   - Assign to users
   - Test access control

4. **Develop Additional Endpoints**
   - Itinerary management
   - Destination management
   - Tour packages
   - etc.

---

## Development Workflow

1. Make code changes
2. Server auto-reloads (if using `--reload`)
3. Test in Swagger UI or with curl
4. Check logs in terminal
5. Iterate

---

## Stopping the Server

Press `Ctrl+C` in the terminal where uvicorn is running.

---

**Ready to start!** 🚀

Run: `uvicorn app.main:app --reload`
