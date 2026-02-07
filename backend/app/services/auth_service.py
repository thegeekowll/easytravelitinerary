"""
Authentication service module.

Handles user authentication, registration, and permission management.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRoleEnum
from app.models.permission import Permission
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import verify_password, get_password_hash, validate_password_strength


class AuthService:
    """Service for authentication and user management."""

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            email: User's email address
            password: Plain text password
            db: Database session

        Returns:
            User object if authentication successful, None otherwise

        Example:
            user = AuthService.authenticate_user("agent@example.com", "password123", db)
            if user:
                # Generate JWT token
                token = create_access_token({"sub": str(user.id)})
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def create_user(user_data: UserCreate, db: Session, created_by_id: Optional[UUID] = None) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data
            db: Database session
            created_by_id: UUID of user creating this user (for admin tracking)

        Returns:
            Created User object

        Raises:
            HTTPException: If email already exists or password is weak

        Example:
            user_data = UserCreate(
                email="newagent@example.com",
                full_name="John Doe",
                password="SecurePass123!",
                role="cs_agent"
            )
            user = AuthService.create_user(user_data, db)
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Validate password strength
        is_valid, error_message = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=user_data.is_active
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Assign permissions if provided
        if user_data.permission_ids:
            AuthService.assign_permissions(db_user.id, user_data.permission_ids, db)

        return db_user

    @staticmethod
    def update_user(user_id: UUID, user_data: UserUpdate, db: Session) -> User:
        """
        Update an existing user.

        Args:
            user_id: User UUID
            user_data: User update data
            db: Database session

        Returns:
            Updated User object

        Raises:
            HTTPException: If user not found or email already exists

        Example:
            update_data = UserUpdate(full_name="Jane Doe")
            user = AuthService.update_user(user_id, update_data, db)
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if email is being updated and if it's already taken
        if user_data.email and user_data.email != user.email:
            existing = db.query(User).filter(User.email == user_data.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )

        # Update fields
        update_dict = user_data.model_dump(exclude_unset=True)

        # Handle password separately
        if "password" in update_dict:
            password = update_dict.pop("password")
            if password:
                # Validate password strength
                is_valid, error_message = validate_password_strength(password)
                if not is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_message
                    )
                user.hashed_password = get_password_hash(password)

        # Handle permissions separately
        if "permission_ids" in update_dict:
            permission_ids = update_dict.pop("permission_ids")
            if permission_ids is not None:
                AuthService.assign_permissions(user.id, permission_ids, db)

        # Update remaining fields
        for field, value in update_dict.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_permissions(user: User) -> List[Permission]:
        """
        Get all permissions for a user.

        Args:
            user: User object with permissions relationship loaded

        Returns:
            List of Permission objects

        Example:
            permissions = AuthService.get_user_permissions(user)
            permission_names = [p.name for p in permissions]
        """
        # Admins have all permissions
        if user.role == UserRoleEnum.ADMIN:
            # Return all available permissions
            from sqlalchemy.orm import Session
            # Note: This requires db session, consider refactoring if needed
            return user.permissions

        return user.permissions

    @staticmethod
    def assign_permissions(user_id: UUID, permission_ids: List[UUID], db: Session) -> User:
        """
        Assign permissions to a user.

        Args:
            user_id: User UUID
            permission_ids: List of permission UUIDs to assign
            db: Database session

        Returns:
            Updated User object

        Raises:
            HTTPException: If user or any permission not found

        Example:
            permission_ids = [perm1_id, perm2_id]
            user = AuthService.assign_permissions(user_id, permission_ids, db)
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get all permissions
        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()

        if len(permissions) != len(permission_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more permissions not found"
            )

        # Replace current permissions with new ones
        user.permissions = permissions

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def add_permissions(user_id: UUID, permission_ids: List[UUID], db: Session) -> User:
        """
        Add permissions to a user (without removing existing ones).

        Args:
            user_id: User UUID
            permission_ids: List of permission UUIDs to add
            db: Database session

        Returns:
            Updated User object

        Raises:
            HTTPException: If user or any permission not found
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get new permissions
        new_permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()

        if len(new_permissions) != len(permission_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more permissions not found"
            )

        # Add new permissions to existing ones (avoiding duplicates)
        existing_ids = {p.id for p in user.permissions}
        for perm in new_permissions:
            if perm.id not in existing_ids:
                user.permissions.append(perm)

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def remove_permissions(user_id: UUID, permission_ids: List[UUID], db: Session) -> User:
        """
        Remove permissions from a user.

        Args:
            user_id: User UUID
            permission_ids: List of permission UUIDs to remove
            db: Database session

        Returns:
            Updated User object

        Raises:
            HTTPException: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Remove specified permissions
        user.permissions = [p for p in user.permissions if p.id not in permission_ids]

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete_user(user_id: UUID, db: Session, soft_delete: bool = True) -> bool:
        """
        Delete a user (soft delete by default).

        Args:
            user_id: User UUID
            db: Database session
            soft_delete: If True, just deactivate; if False, permanently delete

        Returns:
            True if deletion successful

        Raises:
            HTTPException: If user not found

        Example:
            # Soft delete (deactivate)
            AuthService.delete_user(user_id, db)

            # Hard delete (permanent)
            AuthService.delete_user(user_id, db, soft_delete=False)
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if soft_delete:
            # Soft delete: deactivate user
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.commit()
        else:
            # Hard delete: permanently remove
            db.delete(user)
            db.commit()

        return True

    @staticmethod
    def reactivate_user(user_id: UUID, db: Session) -> User:
        """
        Reactivate a deactivated user.

        Args:
            user_id: User UUID
            db: Database session

        Returns:
            Reactivated User object

        Raises:
            HTTPException: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.is_active = True
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def check_user_permission(user: User, permission_name: str) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            user: User object
            permission_name: Name of the permission to check

        Returns:
            True if user has permission, False otherwise

        Example:
            if AuthService.check_user_permission(user, "create_itinerary"):
                # User can create itineraries
                pass
        """
        # Admins have all permissions
        if user.role == UserRoleEnum.ADMIN:
            return True

        # Check specific permissions
        return any(p.name == permission_name for p in user.permissions)

    @staticmethod
    def get_user_by_email(email: str, db: Session) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: Email address
            db: Database session

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(user_id: UUID, db: Session) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User UUID
            db: Database session

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def list_users(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        role: Optional[UserRoleEnum] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        List users with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Filter by role
            is_active: Filter by active status

        Returns:
            List of User objects

        Example:
            # Get all active CS agents
            agents = AuthService.list_users(db, role="cs_agent", is_active=True)
        """
        query = db.query(User)

        if role:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_users(
        db: Session,
        role: Optional[UserRoleEnum] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Count users with optional filtering.

        Args:
            db: Database session
            role: Filter by role
            is_active: Filter by active status

        Returns:
            Total count of matching users
        """
        query = db.query(User)

        if role:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.count()
