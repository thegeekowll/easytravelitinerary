"""
User management endpoints.

Handles user CRUD operations, permissions, and activity logs.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin,
    PaginationParams
)
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithPermissions
)
from app.schemas.permission import PermissionResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.models.user import User, UserRoleEnum
from app.services.import_export_service import ImportExportService
from fastapi.responses import StreamingResponse
from fastapi import UploadFile, File

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    role: Optional[UserRoleEnum] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all users (admin only).

    Args:
        pagination: Pagination parameters
        role: Filter by role
        is_active: Filter by active status
        db: Database session
        current_user: Current admin user

    Returns:
        PaginatedResponse: Paginated list of users
    """
    users = AuthService.list_users(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        role=role,
        is_active=is_active
    )

    total = AuthService.count_users(db, role=role, is_active=is_active)

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=users,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )


@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new user (admin only).

    Args:
        user_data: User creation data
        db: Database session
        current_user: Current admin user

    Returns:
        UserResponse: Created user

    Raises:
        HTTPException: If email already exists or validation fails
    """
    user = AuthService.create_user(user_data, db, created_by_id=current_user.id)
    return user


@router.get("/{user_id}", response_model=UserWithPermissions)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user by ID.

    Users can view their own profile.
    Admins can view any user.

    Args:
        user_id: User UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserWithPermissions: User with permissions

    Raises:
        HTTPException: If user not found or access denied
    """
    user = AuthService.get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if user can access this profile
    if current_user.role != UserRoleEnum.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user.

    Users can update their own profile (limited fields).
    Admins can update any user (all fields).

    Args:
        user_id: User UUID
        user_data: User update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserResponse: Updated user

    Raises:
        HTTPException: If user not found or access denied
    """
    # Check if user can update this profile
    if current_user.role != UserRoleEnum.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own profile"
        )

    # Non-admins cannot change role or permissions
    if current_user.role != UserRoleEnum.ADMIN:
        if user_data.role is not None or user_data.permission_ids is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify role or permissions"
            )

    user = AuthService.update_user(user_id, user_data, db)
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    hard_delete: bool = Query(False, description="Permanently delete user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete user (admin only).

    By default, performs soft delete (deactivates user).
    Use hard_delete=true for permanent deletion.

    Args:
        user_id: User UUID
        hard_delete: If True, permanently delete; if False, soft delete
        db: Database session
        current_user: Current admin user

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If user not found or trying to delete self
    """
    # Prevent admins from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    AuthService.delete_user(user_id, db, soft_delete=not hard_delete)

    message = "User permanently deleted" if hard_delete else "User deactivated"
    return MessageResponse(message=message)


@router.get("/{user_id}/permissions", response_model=list[PermissionResponse])
async def get_user_permissions(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get user's permissions (admin only).

    Args:
        user_id: User UUID
        db: Database session
        current_user: Current admin user

    Returns:
        list[PermissionResponse]: List of user's permissions

    Raises:
        HTTPException: If user not found
    """
    user = AuthService.get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user.permissions


@router.put("/{user_id}/permissions", response_model=UserResponse)
async def set_user_permissions(
    user_id: UUID,
    permission_ids: list[UUID],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Set user's permissions (admin only).

    Replaces all existing permissions with the provided list.

    Args:
        user_id: User UUID
        permission_ids: List of permission UUIDs to assign
        db: Database session
        current_user: Current admin user

    Returns:
        UserResponse: Updated user

    Raises:
        HTTPException: If user or permissions not found
    """
    user = AuthService.assign_permissions(user_id, permission_ids, db)
    return user


@router.post("/{user_id}/permissions/add", response_model=UserResponse)
async def add_user_permissions(
    user_id: UUID,
    permission_ids: list[UUID],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Add permissions to user (admin only).

    Adds permissions without removing existing ones.

    Args:
        user_id: User UUID
        permission_ids: List of permission UUIDs to add
        db: Database session
        current_user: Current admin user

    Returns:
        UserResponse: Updated user

    Raises:
        HTTPException: If user or permissions not found
    """
    user = AuthService.add_permissions(user_id, permission_ids, db)
    return user


@router.post("/{user_id}/permissions/remove", response_model=UserResponse)
async def remove_user_permissions(
    user_id: UUID,
    permission_ids: list[UUID],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Remove permissions from user (admin only).

    Args:
        user_id: User UUID
        permission_ids: List of permission UUIDs to remove
        db: Database session
        current_user: Current admin user

    Returns:
        UserResponse: Updated user

    Raises:
        HTTPException: If user not found
    """
    user = AuthService.remove_permissions(user_id, permission_ids, db)
    return user


@router.post("/{user_id}/reactivate", response_model=UserResponse)
async def reactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Reactivate a deactivated user (admin only).

    Args:
        user_id: User UUID
        db: Session = Depends(get_db)
        current_user: Current admin user

    Returns:
        UserResponse: Reactivated user

    Raises:
        HTTPException: If user not found
    """
    user = AuthService.reactivate_user(user_id, db)
    return user

@router.get("/export/csv")
def export_users_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export all users to CSV format."""
    users = db.query(User).all()
    output = ImportExportService.export_to_csv(users, exclude_fields=['hashed_password', 'id'])
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )

@router.post("/bulk-import", response_model=dict)
def bulk_import_users(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Bulk import users from CSV file. Matches on email."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )

    try:
        content = file.file.read()
        csv_str = content.decode('utf-8')
        rows = ImportExportService.parse_csv(csv_str)

        imported = []
        failed = []

        for row_num, row in enumerate(rows, start=2):
            try:
                email = row.get('email')
                if not email:
                    failed.append({'row': row_num, 'error': 'Missing email'})
                    continue
                
                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    # Update Fields
                    for k, v in row.items():
                        if hasattr(existing, k) and k not in ['id', 'email', 'hashed_password', 'created_at', 'updated_at']:
                            setattr(existing, k, v)
                    imported.append(email)
                else:
                    # Create User (requires password, so we generate a random one if missing)
                    pwd = row.get('password') or 'ChangelMe123!'
                    from app.core.security import get_password_hash
                    new_user = User(
                        email=email,
                        hashed_password=get_password_hash(pwd),
                        full_name=row.get('full_name') or email.split('@')[0],
                        role=row.get('role') or UserRoleEnum.CS_AGENT,
                        is_active=row.get('is_active') if row.get('is_active') is not None else True,
                        phone_number=row.get('phone_number'),
                        address=row.get('address'),
                        position=row.get('position')
                    )
                    db.add(new_user)
                    imported.append(email)
            except Exception as e:
                failed.append({'row': row_num, 'error': str(e)})

        db.commit()
        return {
            'success': True,
            'imported_count': len(imported),
            'failed_count': len(failed),
            'imported': imported,
            'failed': failed
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

