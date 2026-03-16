# Travel Agency Platform - Deployment Guide

This document provides comprehensive instructions for deploying the Travel Agency Management System to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Local Development](#local-development)
4. [Production Deployment](#production-deployment)
5. [Database Migrations](#database-migrations)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- Docker & Docker Compose (v2.20+)
- PostgreSQL 16
- Redis 7
- Python 3.11+
- Node.js 18+ (for frontend)
- Git

### Cloud Services

- **Azure Blob Storage** - For file uploads (PDFs, images)
- **SendGrid** - For email delivery
- **SSL Certificate** - For HTTPS (Let's Encrypt recommended)

---

## Environment Variables

### Backend (.env)

Create `/backend/.env` file with the following variables:

```bash
# Application
APP_NAME=Travel Agency Management System
ENVIRONMENT=production  # development, staging, production
DEBUG=False
SECRET_KEY=your-super-secret-key-min-32-chars

# Server
HOST=0.0.0.0
PORT=8000

# Database
POSTGRES_SERVER=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong-password-here
POSTGRES_DB=travel_agency

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]

# Frontend URL
FRONTEND_URL=https://yourdomain.com

# SendGrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAILS_FROM_EMAIL=noreply@yourdomain.com
EMAILS_FROM_NAME=Travel Agency

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER=travel-agency-uploads

# Password Requirements
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_DIGIT=True
PASSWORD_REQUIRE_SPECIAL=True

# API Settings
API_V1_PREFIX=/api/v1
```

### Frontend (.env.local)

Create `/frontend/.env.local` file:

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_URL=https://yourdomain.com
```

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/your-org/travel-agency-platform.git
cd travel-agency-platform
```

### 2. Set Up Environment Variables

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your local settings

# Frontend
cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local with your local settings
```

### 3. Start Services with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Run Database Migrations

```bash
# Create initial migration
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Seed database (optional)
docker-compose exec backend python seed_data.py
```

### 5. Access Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## Production Deployment

### Option 1: Docker Compose on VPS

#### 1. Server Setup

```bash
# SSH into your server
ssh user@your-server.com

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/your-org/travel-agency-platform.git
cd travel-agency-platform

# Set up environment variables
nano backend/.env
nano frontend/.env.local

# Set production values
```

#### 3. Deploy

```bash
# Build and start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed initial data (if needed)
docker-compose exec backend python seed_data.py
```

#### 4. Set Up Nginx Reverse Proxy

Create `/etc/nginx/sites-available/travel-agency`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Documentation
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

Enable and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/travel-agency /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

### Option 2: GitHub Actions CI/CD

The project includes automated deployment via GitHub Actions.

#### 1. Set Up GitHub Secrets

Go to your repository → Settings → Secrets and add:

- `DEPLOY_HOST`: Production server IP
- `DEPLOY_USER`: SSH username
- `DEPLOY_SSH_KEY`: Private SSH key for deployment
- `STAGING_HOST`: Staging server IP
- `STAGING_USER`: Staging SSH username
- `STAGING_SSH_KEY`: Staging SSH private key
- `PRODUCTION_URL`: https://yourdomain.com
- `STAGING_URL`: https://staging.yourdomain.com
- `SLACK_WEBHOOK`: (Optional) Slack notification webhook

#### 2. Workflow Triggers

- **Push to `main`**: Deploys to production
- **Push to `develop`**: Deploys to staging
- **Pull Request**: Runs tests only

#### 3. Manual Deployment

```bash
# Trigger workflow manually
gh workflow run deploy.yml
```

---

## Database Migrations

### Create New Migration

```bash
# Generate migration from model changes
docker-compose exec backend alembic revision --autogenerate -m "Add new feature"

# Review generated migration in backend/alembic/versions/
```

### Apply Migrations

```bash
# Apply all pending migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history
```

### Seeding Data

```bash
# Run seed script
docker-compose exec backend python seed_data.py

# The script creates:
# - Default admin user
# - Sample destinations
# - Sample accommodations
# - Sample base tours
```

---

## Monitoring and Logging

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Health Checks

```bash
# Backend health
curl https://yourdomain.com/health

# Database check
curl https://yourdomain.com/db-check
```

### Scheduled Jobs

The system includes APScheduler for:

- **3-day arrival notifications**: Runs daily at 9 AM
- Checks for itineraries departing in 3 days
- Sends high-priority notifications to assigned agents

View scheduler logs:

```bash
docker-compose logs -f backend | grep "APScheduler"
```

---

## Backup and Restore

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres travel_agency > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T postgres psql -U postgres travel_agency < backup_20240115.sql
```

### Azure Blob Storage Backup

Azure Blob Storage has built-in redundancy. Configure geo-replication in Azure Portal for additional protection.

---

## Troubleshooting

### Issue: Backend won't start

**Check logs:**
```bash
docker-compose logs backend
```

**Common causes:**
- Database not ready → Wait for `postgres` health check
- Missing environment variables → Check `.env` file
- Port already in use → Change port in `docker-compose.yml`

### Issue: PDF generation fails

**Check Playwright:**
```bash
docker-compose exec backend playwright install chromium
```

**Check logs:**
```bash
docker-compose logs backend | grep "PDF"
```

### Issue: Emails not sending

**Verify SendGrid:**
- API key is correct in `.env`
- Sender email is verified in SendGrid dashboard
- Check SendGrid activity logs

### Issue: Database connection errors

**Check PostgreSQL:**
```bash
docker-compose exec postgres psql -U postgres -c "SELECT 1"
```

**Verify connection string in `.env`:**
```
DATABASE_URL=postgresql://postgres:password@postgres:5432/travel_agency
```

### Issue: Redis connection errors

**Check Redis:**
```bash
docker-compose exec redis redis-cli ping
```

Should return `PONG`.

---

## Production Checklist

- [ ] Environment variables set in production `.env`
- [ ] Strong passwords for database and JWT secrets
- [ ] SendGrid API key configured and sender verified
- [ ] Azure Blob Storage connection string configured
- [ ] SSL certificate installed and auto-renewal configured
- [ ] Firewall configured (allow 80, 443, SSH only)
- [ ] Database backups scheduled (daily recommended)
- [ ] Monitoring set up (optional: Sentry, DataDog, etc.)
- [ ] Logs rotation configured
- [ ] Default admin password changed
- [ ] CORS origins restricted to production domain
- [ ] Rate limiting configured on Nginx (optional)

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-org/travel-agency-platform/issues
- Email: support@yourdomain.com
