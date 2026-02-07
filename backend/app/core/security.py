"""
Security utilities for authentication and authorization.

This module provides:
- Password hashing and verification
- JWT token creation and validation
- Permission checking decorators
- Role-based access control helpers
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


# ==================== Password Hashing ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


# Alias for compatibility
hash_password = get_password_hash


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength based on settings.

    Args:
        password: Plain text password

    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long"

    if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if settings.PASSWORD_REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    if settings.PASSWORD_REQUIRE_SPECIAL:
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

    return True, None


# ==================== JWT Token Management ====================

def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create JWT access token.

    Args:
        subject: User ID or username
        expires_delta: Optional expiration time delta
        additional_claims: Optional additional claims to include

    Returns:
        str: Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
    }

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create JWT refresh token.

    Args:
        subject: User ID or username
        expires_delta: Optional expiration time delta

    Returns:
        str: Encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify token type and return payload.

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token type doesn't match or token is invalid
    """
    payload = decode_token(token)

    if payload.get("type") != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {token_type}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# ==================== Authentication Dependencies ====================

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Get current user ID from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        str: User ID (UUID string)

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = verify_token(token, "access")

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get current user from database.

    Args:
        user_id: User ID from token (UUID string)
        db: Database session

    Returns:
        User: Current user object

    Raises:
        HTTPException: If user not found or inactive
    """
    from app.models.user import User
    from uuid import UUID

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    return user


async def get_current_active_user(
    current_user = Depends(get_current_user),
):
    """
    Get current active user.

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is inactive
    """
    # TODO: Update when User model is created
    # if not current_user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Inactive user"
    #     )
    return current_user


# ==================== Role-Based Access Control ====================

class RoleChecker:
    """
    Dependency class to check if user has required role.

    Usage:
        @router.get("/admin")
        async def admin_route(user = Depends(RoleChecker(["admin"]))):
            return {"message": "Admin access granted"}
    """

    def __init__(self, allowed_roles: List[str]):
        """
        Initialize role checker.

        Args:
            allowed_roles: List of allowed role names
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user = Depends(get_current_user)):
        """
        Check if user has required role.

        Args:
            current_user: Current user from dependency

        Returns:
            User: Current user if role check passes

        Raises:
            HTTPException: If user doesn't have required role
        """
        # TODO: Update when User model with roles is created
        # if current_user.role.name not in self.allowed_roles:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not enough permissions"
        #     )
        return current_user


class PermissionChecker:
    """
    Dependency class to check if user has required permission.

    Usage:
        @router.post("/itineraries")
        async def create_itinerary(
            user = Depends(PermissionChecker(["itinerary:create"]))
        ):
            return {"message": "Permission granted"}
    """

    def __init__(self, required_permissions: List[str]):
        """
        Initialize permission checker.

        Args:
            required_permissions: List of required permission codes
        """
        self.required_permissions = required_permissions

    async def __call__(self, current_user = Depends(get_current_user)):
        """
        Check if user has required permissions.

        Args:
            current_user: Current user from dependency

        Returns:
            User: Current user if permission check passes

        Raises:
            HTTPException: If user doesn't have required permissions
        """
        # TODO: Update when User model with permissions is created
        # user_permissions = [p.code for p in current_user.role.permissions]
        # for permission in self.required_permissions:
        #     if permission not in user_permissions:
        #         raise HTTPException(
        #             status_code=status.HTTP_403_FORBIDDEN,
        #             detail=f"Missing required permission: {permission}"
        #         )
        return current_user


# ==================== Helper Functions ====================

def has_role(user, role_name: str) -> bool:
    """
    Check if user has a specific role.

    Args:
        user: User object
        role_name: Role name to check

    Returns:
        bool: True if user has the role
    """
    # TODO: Update when User model is created
    # return user.role.name == role_name
    return True


def has_permission(user, permission_code: str) -> bool:
    """
    Check if user has a specific permission.

    Args:
        user: User object
        permission_code: Permission code to check

    Returns:
        bool: True if user has the permission
    """
    # TODO: Update when User model is created
    # user_permissions = [p.code for p in user.role.permissions]
    # return permission_code in user_permissions
    return True


def has_any_role(user, role_names: List[str]) -> bool:
    """
    Check if user has any of the specified roles.

    Args:
        user: User object
        role_names: List of role names to check

    Returns:
        bool: True if user has any of the roles
    """
    # TODO: Update when User model is created
    # return user.role.name in role_names
    return True


def has_all_permissions(user, permission_codes: List[str]) -> bool:
    """
    Check if user has all specified permissions.

    Args:
        user: User object
        permission_codes: List of permission codes to check

    Returns:
        bool: True if user has all permissions
    """
    # TODO: Update when User model is created
    # user_permissions = [p.code for p in user.role.permissions]
    # return all(code in user_permissions for code in permission_codes)
    return True


# ==================== Role and Permission Constants ====================

class Roles:
    """Role name constants."""
    ADMIN = "admin"
    CS_AGENT = "cs_agent"
    PUBLIC = "public"


class Permissions:
    """Permission code constants."""
    # User permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Itinerary permissions
    ITINERARY_CREATE = "itinerary:create"
    ITINERARY_READ = "itinerary:read"
    ITINERARY_UPDATE = "itinerary:update"
    ITINERARY_DELETE = "itinerary:delete"
    ITINERARY_GENERATE_PDF = "itinerary:generate_pdf"
    ITINERARY_SEND_EMAIL = "itinerary:send_email"

    # Package permissions
    PACKAGE_CREATE = "package:create"
    PACKAGE_READ = "package:read"
    PACKAGE_UPDATE = "package:update"
    PACKAGE_DELETE = "package:delete"

    # Destination permissions
    DESTINATION_CREATE = "destination:create"
    DESTINATION_READ = "destination:read"
    DESTINATION_UPDATE = "destination:update"
    DESTINATION_DELETE = "destination:delete"

    # Accommodation permissions
    ACCOMMODATION_CREATE = "accommodation:create"
    ACCOMMODATION_READ = "accommodation:read"
    ACCOMMODATION_UPDATE = "accommodation:update"
    ACCOMMODATION_DELETE = "accommodation:delete"

    # Analytics permissions
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"

    # Admin permissions
    SYSTEM_SETTINGS = "system:settings"
    ROLE_MANAGE = "role:manage"
    PERMISSION_MANAGE = "permission:manage"
