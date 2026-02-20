"""
Application configuration settings.
"""
from typing import Any, Dict, List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        env_parse_none_str="None",  # Don't try to parse empty strings as None
        populate_by_name=True,  # Allow both alias and field name
    )

    # Application
    APP_NAME: str = "Travel Agency Management System"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS origins - accepts comma-separated string from env var BACKEND_CORS_ORIGINS
    BACKEND_CORS_ORIGINS_STR: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        alias="BACKEND_CORS_ORIGINS",
    )

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        raw = self.BACKEND_CORS_ORIGINS_STR
        if isinstance(raw, str):
            origins = [i.strip() for i in raw.split(",") if i.strip()]
            if origins:
                return origins
        return ["http://localhost:3000", "http://localhost:8000"]

    # Database
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "travel_agency"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str) and v:
            return v
        # Build connection string from components
        user = info.data.get("POSTGRES_USER", "postgres")
        password = info.data.get("POSTGRES_PASSWORD", "postgres")
        host = info.data.get("POSTGRES_SERVER", "localhost")
        port = info.data.get("POSTGRES_PORT", 5432)
        db = info.data.get("POSTGRES_DB", "travel_agency")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: Optional[str], info) -> str:
        if v:
            return v
        password = info.data.get("REDIS_PASSWORD")
        if password:
            return f"redis://:{password}@{info.data.get('REDIS_HOST')}:{info.data.get('REDIS_PORT')}/{info.data.get('REDIS_DB')}"
        return f"redis://{info.data.get('REDIS_HOST')}:{info.data.get('REDIS_PORT')}/{info.data.get('REDIS_DB')}"

    # JWT
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM_ADDRESS: str = "noreply@youragency.com"
    EMAIL_FROM_NAME: str = "Travel Agency"
    EMAIL_TEMPLATE_DIR: str = "app/templates/email"
    EMAILS_FROM_EMAIL: str = "noreply@youragency.com"  # Alias for compatibility
    EMAILS_FROM_NAME: str = "Travel Agency"  # Alias for compatibility

    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER: str = "travel-agency-files"
    AZURE_STORAGE_ACCOUNT_NAME: Optional[str] = None
    AZURE_STORAGE_ACCOUNT_KEY: Optional[str] = None



    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx"]

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_TIMEZONE: str = "UTC"

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def set_celery_broker(cls, v: Optional[str], info) -> str:
        return v or info.data.get("REDIS_URL") or ""

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def set_celery_backend(cls, v: Optional[str], info) -> str:
        return v or info.data.get("REDIS_URL") or ""

    # Notifications
    NOTIFICATION_CHECK_INTERVAL: int = 3600  # 1 hour in seconds
    ARRIVAL_ALERT_DAYS: int = 3

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # Session
    SESSION_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"

    # Analytics
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_RETENTION_DAYS: int = 365

    # Feature Flags
    ENABLE_PUBLIC_ITINERARY_VIEW: bool = True
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_SMS_NOTIFICATIONS: bool = False
    ENABLE_PAYMENT_TRACKING: bool = True

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT.lower() == "development"


# Create settings instance
settings = Settings()
