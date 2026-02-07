# Setup Guide - Travel Agency Management System

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Local Development Setup](#local-development-setup)
4. [Database Setup](#database-setup)
5. [Environment Configuration](#environment-configuration)
6. [Running the Application](#running-the-application)
7. [Common Issues](#common-issues)

## Prerequisites

### Required Software
- **Docker Desktop**: 4.25+ (recommended for quick start)
- **Node.js**: 20.x or higher
- **Python**: 3.11 or higher
- **PostgreSQL**: 16.x (if running locally)
- **Redis**: 7.x (if running locally)
- **Git**: Latest version

### External Services
You'll need accounts and API keys for:
- **SendGrid**: For email functionality
- **Azure Storage**: For file storage (or you can use local storage for development)

## Quick Start with Docker

This is the fastest way to get the entire stack running.

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Itinerary Builder Platform"
```

### 2. Set Up Environment Variables
```bash
# Copy environment templates
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

### 3. Configure Essential Variables
Edit `.env` and update these critical values:
```bash
# Generate a secure secret key
SECRET_KEY=your-super-secret-key-change-this-in-production

# SendGrid API key (get from SendGrid dashboard)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx

# Azure Storage (or comment out for local storage)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER=travel-agency-files
```

### 4. Build and Start All Services
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- Backend API (FastAPI)
- Frontend application (Next.js)
- Celery worker (async tasks)
- Celery beat (scheduled tasks)

### 5. Initialize the Database
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create initial admin user
docker-compose exec backend python -m app.scripts.create_admin
```

### 6. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 7. Login
Use the admin credentials you created in step 5.

## Local Development Setup

For active development, running services locally provides better debugging and hot-reload capabilities.

### Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/travel_agency

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# SendGrid
SENDGRID_API_KEY=your-sendgrid-api-key

# Azure (optional for dev)
# AZURE_STORAGE_CONNECTION_STRING=your-connection-string
```

#### 5. Start Required Services
```bash
# Start PostgreSQL and Redis via Docker
docker-compose up -d postgres redis
```

#### 6. Run Database Migrations
```bash
alembic upgrade head
```

#### 7. Create Initial Data
```bash
# Create admin user
python -m app.scripts.create_admin

# Load sample data (optional)
python -m app.scripts.load_sample_data
```

#### 8. Start Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd frontend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Set Up Environment Variables
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

#### 4. Start Development Server
```bash
npm run dev
```

The application will be available at http://localhost:3000

### Running Celery Workers (Optional for Dev)

For background tasks and scheduled jobs:

```bash
# In backend directory with venv activated

# Start worker
celery -A app.services.celery_app worker --loglevel=info

# In another terminal, start beat scheduler
celery -A app.services.celery_app beat --loglevel=info
```

## Database Setup

### Creating the Database Manually

If you're not using Docker for PostgreSQL:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE travel_agency;

# Create user (optional)
CREATE USER travel_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE travel_agency TO travel_user;

# Exit
\q
```

### Running Migrations

```bash
cd backend

# Create a new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base
```

## Environment Configuration

### Backend Environment Variables

Key variables to configure in `backend/.env`:

```bash
# Application
APP_NAME=Travel Agency Management System
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=<generate-secure-key>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=<generate-secure-key>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SENDGRID_API_KEY=<your-api-key>
EMAIL_FROM_ADDRESS=noreply@youragency.com

# Storage
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>
AZURE_STORAGE_CONTAINER=travel-agency-files

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Frontend Environment Variables

Key variables to configure in `frontend/.env.local`:

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Features
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_PUBLIC_ITINERARIES=true
```

### Generating Secure Keys

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use openssl
openssl rand -base64 32
```

## Running the Application

### Development Mode

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Celery Worker (optional)
cd backend
source venv/bin/activate
celery -A app.services.celery_app worker --loglevel=info

# Terminal 4 - Celery Beat (optional)
cd backend
source venv/bin/activate
celery -A app.services.celery_app beat --loglevel=info
```

### Production Mode with Docker

```bash
# Build and start all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Common Issues

### Port Already in Use

```bash
# Check what's using the port
# On macOS/Linux:
lsof -i :8000  # or :3000, :5432, :6379

# On Windows:
netstat -ano | findstr :8000

# Kill the process or change port in configuration
```

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Connect to database manually
docker-compose exec postgres psql -U postgres -d travel_agency
```

### Redis Connection Errors

```bash
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should respond: PONG
```

### Module Import Errors (Python)

```bash
# Ensure virtual environment is activated
which python  # Should point to your venv

# Reinstall dependencies
pip install -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
```

### Node Module Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
npm run build
```

### Alembic Migration Errors

```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Stamp to a specific version (if out of sync)
alembic stamp head

# Reset database (DEVELOPMENT ONLY)
alembic downgrade base
alembic upgrade head
```

### Docker Issues

```bash
# Remove all containers and volumes (CAUTION: deletes data)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache

# View container logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute commands in container
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Permission Errors

```bash
# Fix file permissions (on Linux/macOS)
sudo chown -R $USER:$USER .

# Docker permission issues
sudo usermod -aG docker $USER
# Then log out and back in
```

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_auth.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm test -- --coverage
```

## Next Steps

1. Review the [README.md](README.md) for feature overview
2. Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for codebase organization
3. Explore the API documentation at http://localhost:8000/api/v1/docs
4. Start building features or customizing the application

## Getting Help

- Check the logs: `docker-compose logs -f`
- Review the documentation in `/docs`
- Check GitHub issues
- Contact the development team

## Useful Commands Cheat Sheet

```bash
# Docker
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose ps                 # List running services
docker-compose logs -f [service]  # View logs

# Backend
alembic upgrade head              # Run migrations
alembic revision --autogenerate   # Create migration
pytest                            # Run tests
black app/                        # Format code

# Frontend
npm run dev                       # Start dev server
npm run build                     # Build for production
npm run lint                      # Lint code
npm run format                    # Format code

# Database
docker-compose exec postgres psql -U postgres -d travel_agency
docker-compose exec backend alembic current
docker-compose exec backend python -m app.scripts.create_admin
```
