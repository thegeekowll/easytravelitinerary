"""
Authentication endpoints.

Handles login, token refresh, and user profile retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api.v1.deps import get_db, get_current_active_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.services.auth_service import AuthService
from app.schemas.user import UserResponse, UserWithPermissions
from app.schemas.common import MessageResponse
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password.

    Returns access token and refresh token.

    Args:
        form_data: OAuth2 form with username (email) and password
        db: Database session

    Returns:
        dict: Access token, refresh token, and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = AuthService.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    # Create access and refresh tokens
    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={"role": user.role.value}
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserWithPermissions.model_validate(user)
    }


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Args:
        refresh_token: Refresh token string
        db: Database session

    Returns:
        dict: New access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        payload = verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Get user from database
        from uuid import UUID
        user = AuthService.get_user_by_id(UUID(user_id), db)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={"role": user.role.value}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserWithPermissions)
async def get_current_user_profile(
    current_user = Depends(get_current_active_user)
):
    """
    Get current user's profile with permissions.

    Args:
        current_user: Current authenticated user

    Returns:
        UserWithPermissions: User profile with permissions
    """
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user = Depends(get_current_active_user)
):
    """
    Logout current user.

    Note: JWT tokens are stateless, so this is primarily for client-side cleanup.
    In a production environment, you might want to implement token blacklisting.

    Args:
        current_user: Current authenticated user

    Returns:
        MessageResponse: Success message
    """
    return MessageResponse(message="Successfully logged out")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Request password reset email.

    Args:
        email: User's email address
        db: Database session

    Returns:
        MessageResponse: Always returns success (for security, don't reveal if email exists)
    """
    user = AuthService.get_user_by_email(email, db)

    if user:
        # TODO: Generate reset token and send email
        # For now, just return success
        # In production:
        # 1. Generate unique reset token
        # 2. Store token in database with expiration
        # 3. Send email with reset link
        pass

    # Always return success for security (don't reveal if email exists)
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset token.

    Args:
        token: Password reset token
        new_password: New password
        db: Database session

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    # TODO: Implement password reset logic
    # For now, return not implemented
    # In production:
    # 1. Verify reset token
    # 2. Find user by token
    # 3. Update password
    # 4. Invalidate reset token

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset not yet implemented"
    )
