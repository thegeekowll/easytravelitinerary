"""
Database session configuration.
"""
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create SQLAlchemy engine
# Use NullPool for serverless/Azure deployments to avoid connection pool issues
engine = create_engine(
    str(settings.DATABASE_URL),
    poolclass=NullPool if settings.is_production else None,
    pool_pre_ping=True,  # Verify connections before using them
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,
)


# Optional: Set timezone for PostgreSQL connections
@event.listens_for(engine, "connect")
def set_timezone(dbapi_conn, connection_record):
    """Set timezone to UTC for all database connections."""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET TIME ZONE 'UTC'")
    cursor.close()


# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Usage in FastAPI endpoints:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_async() -> Generator[Session, None, None]:
    """
    Async version of get_db dependency.

    Usage in async FastAPI endpoints:
        @router.get("/items")
        async def get_items(db: Session = Depends(get_db_async)):
            return db.query(Item).all()

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
