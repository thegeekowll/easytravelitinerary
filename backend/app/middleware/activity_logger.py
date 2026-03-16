"""
Activity logging middleware.

Logs all user actions to the ActivityLog table for audit trail.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from datetime import datetime
from typing import Callable
import json

from app.models.activity_log import ActivityLog
from app.db.session import SessionLocal


class ActivityLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log user activity for audit trail.

    Logs:
    - User actions (create, update, delete)
    - Endpoint accessed
    - Request method
    - IP address
    - Timestamp
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and log activity."""

        # Skip logging for certain endpoints
        skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/favicon.ico",
            "/_next",  # Next.js static files
            "/static",
        ]

        should_skip = any(request.url.path.startswith(path) for path in skip_paths)

        # Skip logging for GET requests (read-only operations)
        # Only log: POST, PUT, PATCH, DELETE (write operations)
        should_log = request.method in ["POST", "PUT", "PATCH", "DELETE"]

        # Process request
        response = await call_next(request)

        # Log activity if applicable
        if should_log and not should_skip and response.status_code < 400:
            try:
                await self._log_activity(request, response)
            except Exception as e:
                # Don't fail the request if logging fails
                print(f"Activity logging failed: {str(e)}")

        return response

    async def _log_activity(self, request: Request, response):
        """Log activity to database."""

        # Extract user from Authorization header
        user = await self._get_user_from_token(request)

        if not user:
            # No authenticated user, skip logging
            return

        # Determine action type based on method
        action_map = {
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        action = action_map.get(request.method, "unknown")

        # Extract entity type from URL
        entity_type = self._extract_entity_type(request.url.path)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Build description
        description = f"{action.capitalize()} {entity_type} via {request.method} {request.url.path}"

        # Extract entity ID if present in path
        entity_id = self._extract_entity_id(request.url.path)

        # Create log entry
        db = SessionLocal()
        try:
            activity_log = ActivityLog(
                user_id=user.id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent", "")[:500],
                created_at=datetime.utcnow()
            )

            db.add(activity_log)
            db.commit()

        except Exception as e:
            db.rollback()
            print(f"Failed to log activity: {str(e)}")
        finally:
            db.close()

    def _extract_entity_type(self, path: str) -> str:
        """Extract entity type from URL path."""

        # Map URL paths to entity types
        entity_map = {
            "/api/v1/destinations": "destination",
            "/api/v1/accommodations": "accommodation",
            "/api/v1/base-tours": "base_tour",
            "/api/v1/itineraries": "itinerary",
            "/api/v1/users": "user",
            "/api/v1/content": "content",
            "/api/v1/media": "media",
            "/api/v1/destination-combinations": "destination_combination",
            "/api/v1/notifications": "notification",
        }

        for url_pattern, entity_type in entity_map.items():
            if path.startswith(url_pattern):
                return entity_type

        return "unknown"

    def _extract_entity_id(self, path: str) -> str | None:
        """Extract entity ID from URL path."""

        # Split path and look for UUID-like segments
        import re
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

        match = re.search(uuid_pattern, path)
        if match:
            return match.group(0)

        return None

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""

        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        if request.client:
            return request.client.host

        return "unknown"

    async def _get_user_from_token(self, request: Request):
        """Extract user from authorization header."""
        from jose import jwt, JWTError
        from app.core.config import settings
        from app.models.user import User
        from uuid import UUID

        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "")

        try:
            # Decode token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            user_id = payload.get("sub")
            if not user_id:
                return None

            # Get user from database
            db = SessionLocal()
            try:
                user_uuid = UUID(user_id)
                user = db.query(User).filter(User.id == user_uuid).first()
                return user
            finally:
                db.close()

        except (JWTError, ValueError, Exception):
            return None


def add_activity_logger_middleware(app):
    """Add activity logger middleware to FastAPI app."""
    app.add_middleware(ActivityLoggerMiddleware)
