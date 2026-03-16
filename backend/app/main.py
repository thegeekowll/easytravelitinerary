"""
FastAPI application main module.
"""
import secrets
import string

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db, engine, SessionLocal
from app.api.v1.api import api_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Travel Agency Management System API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Configure CORS
_cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=("*" not in _cors_origins),  # credentials not allowed with wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add activity logger middleware
from app.middleware.activity_logger import add_activity_logger_middleware
add_activity_logger_middleware(app)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Mount static files for local uploads (development only)
from fastapi.staticfiles import StaticFiles
import os

# Create uploads directory if not exists
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("=" * 70)
    print(f" {settings.APP_NAME}")
    print("=" * 70)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug: {settings.DEBUG}")
    print(f"Database: {settings.POSTGRES_DB}")
    print("=" * 70)

    # Create default admin user if none exists
    try:
        import os
        from app.models.user import User, UserRoleEnum
        from app.core.security import get_password_hash

        db = SessionLocal()
        try:
            admin_count = db.query(User).filter(User.role == UserRoleEnum.ADMIN).count()

            if admin_count == 0:
                # Use env var if provided, otherwise generate a random password
                admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "")
                if not admin_password:
                    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
                    admin_password = ''.join(secrets.choice(alphabet) for _ in range(16))

                default_admin = User(
                    email=os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@travelagency.com"),
                    full_name="System Administrator",
                    hashed_password=get_password_hash(admin_password),
                    role=UserRoleEnum.ADMIN,
                    is_active=True
                )
                db.add(default_admin)
                db.commit()
                print("\n" + "=" * 60)
                print("  DEFAULT ADMIN ACCOUNT CREATED")
                print("=" * 60)
                print(f"  Email:    {default_admin.email}")
                print(f"  Password: {admin_password}")
                print("  ** Save this password now — it will not be shown again **")
                print("=" * 60 + "\n")
        finally:
            db.close()
    except Exception as e:
        print(f"Could not create default admin: {e}")

    # Start scheduled job for 3-day arrival notifications
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        from app.services.notification_service import notification_service

        async def check_arrivals_job():
            """Scheduled job to check for upcoming arrivals."""
            db = SessionLocal()
            try:
                result = await notification_service.check_upcoming_arrivals(db)
                print(f"✅ Checked arrivals: {result['itineraries_found']} found")
            except Exception as e:
                print(f"⚠️  Error checking arrivals: {e}")
            finally:
                db.close()

        scheduler = AsyncIOScheduler()
        # Run daily at 9 AM
        scheduler.add_job(
            check_arrivals_job,
            CronTrigger(hour=9, minute=0),
            id='check_3_day_arrivals',
            name='Check 3-Day Arrival Notifications',
            replace_existing=True
        )
        scheduler.start()
        print("\n✅ Scheduled job started: 3-day arrival notifications (daily at 9 AM)")

    except Exception as e:
        print(f"⚠️  Could not start scheduled jobs: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("\nShutting down application...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Travel Agency Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/db-check")
async def database_check(db: Session = Depends(get_db)):
    """Database connection check endpoint (admin-only details omitted)."""
    try:
        result = db.execute(text("SELECT 1"))
        result.scalar()
        return {"status": "connected"}
    except Exception:
        return {"status": "error"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
