"""
Custom exception classes for the application.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class BadRequestException(AppException):
    """Bad request exception."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UnauthorizedException(AppException):
    """Unauthorized exception."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    """Forbidden exception."""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class ConflictException(AppException):
    """Conflict exception."""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ValidationException(AppException):
    """Validation exception."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InternalServerException(AppException):
    """Internal server error exception."""

    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class ServiceUnavailableException(AppException):
    """Service unavailable exception."""

    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )


# Specific business logic exceptions

class UserNotFoundException(NotFoundException):
    """User not found exception."""

    def __init__(self, user_id: int = None):
        detail = f"User with ID {user_id} not found" if user_id else "User not found"
        super().__init__(detail=detail)


class UserAlreadyExistsException(ConflictException):
    """User already exists exception."""

    def __init__(self, email: str = None):
        detail = f"User with email {email} already exists" if email else "User already exists"
        super().__init__(detail=detail)


class InvalidCredentialsException(UnauthorizedException):
    """Invalid credentials exception."""

    def __init__(self):
        super().__init__(detail="Invalid email or password")


class InactiveUserException(ForbiddenException):
    """Inactive user exception."""

    def __init__(self):
        super().__init__(detail="User account is inactive")


class ItineraryNotFoundException(NotFoundException):
    """Itinerary not found exception."""

    def __init__(self, itinerary_id: int = None):
        detail = (
            f"Itinerary with ID {itinerary_id} not found"
            if itinerary_id
            else "Itinerary not found"
        )
        super().__init__(detail=detail)


class PackageNotFoundException(NotFoundException):
    """Package not found exception."""

    def __init__(self, package_id: int = None):
        detail = (
            f"Package with ID {package_id} not found" if package_id else "Package not found"
        )
        super().__init__(detail=detail)


class DestinationNotFoundException(NotFoundException):
    """Destination not found exception."""

    def __init__(self, destination_id: int = None):
        detail = (
            f"Destination with ID {destination_id} not found"
            if destination_id
            else "Destination not found"
        )
        super().__init__(detail=detail)


class PermissionDeniedException(ForbiddenException):
    """Permission denied exception."""

    def __init__(self, permission: str = None):
        detail = (
            f"Permission denied: {permission}" if permission else "You don't have permission to perform this action"
        )
        super().__init__(detail=detail)


class InvalidTokenException(UnauthorizedException):
    """Invalid token exception."""

    def __init__(self):
        super().__init__(detail="Invalid or expired token")


class TokenExpiredException(UnauthorizedException):
    """Token expired exception."""

    def __init__(self):
        super().__init__(detail="Token has expired")
