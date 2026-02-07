"""
API dependencies.

This module contains common dependencies used across API endpoints.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import (
    get_current_user,
    get_current_active_user,
    get_current_user_id,
    RoleChecker,
    PermissionChecker,
    Roles,
)

# ==================== Database Dependencies ====================

def get_db_session() -> Generator[Session, None, None]:
    """
    Get database session dependency.
    Alias for get_db for clarity in endpoint usage.
    """
    yield from get_db()


# ==================== Authentication Dependencies ====================

def get_current_user_dep(
    current_user = Depends(get_current_user),
):
    """
    Get current authenticated user.

    Usage:
        @router.get("/me")
        def read_current_user(user = Depends(get_current_user_dep)):
            return user
    """
    return current_user


def get_current_active_user_dep(
    current_user = Depends(get_current_active_user),
):
    """
    Get current active user.

    Usage:
        @router.get("/profile")
        def read_profile(user = Depends(get_current_active_user_dep)):
            return user
    """
    return current_user


# ==================== Role-Based Dependencies ====================

def require_admin(
    current_user = Depends(RoleChecker([Roles.ADMIN])),
):
    """
    Require admin role.

    Usage:
        @router.get("/admin/users")
        def list_users(user = Depends(require_admin)):
            return users
    """
    return current_user


def require_cs_agent(
    current_user = Depends(RoleChecker([Roles.CS_AGENT, Roles.ADMIN])),
):
    """
    Require CS agent or admin role.

    Usage:
        @router.post("/itineraries")
        def create_itinerary(user = Depends(require_cs_agent)):
            return itinerary
    """
    return current_user


def require_authenticated(
    current_user = Depends(get_current_active_user),
):
    """
    Require any authenticated user.

    Usage:
        @router.get("/profile")
        def get_profile(user = Depends(require_authenticated)):
            return profile
    """
    return current_user


# ==================== Permission-Based Dependencies ====================

def require_permission(*permissions: str):
    """
    Factory function to create permission checker dependency.

    Usage:
        @router.post("/itineraries")
        def create_itinerary(
            user = Depends(require_permission("itinerary:create"))
        ):
            return itinerary

    Note: Returns a PermissionChecker instance that should be wrapped in Depends()
    """
    return PermissionChecker(list(permissions))


# ==================== Pagination Dependencies ====================

class PaginationParams:
    """
    Pagination parameters for list endpoints.

    Usage:
        @router.get("/items")
        def list_items(pagination: PaginationParams = Depends()):
            return db.query(Item).offset(pagination.skip).limit(pagination.limit).all()
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
        self.limit = page_size


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict:
    """
    Get pagination parameters.

    Returns:
        dict: Contains page, page_size, skip, and limit
    """
    return {
        "page": page,
        "page_size": page_size,
        "skip": (page - 1) * page_size,
        "limit": page_size,
    }


# ==================== Sorting Dependencies ====================

class SortParams:
    """
    Sorting parameters for list endpoints.

    Usage:
        @router.get("/items")
        def list_items(sort: SortParams = Depends()):
            query = db.query(Item)
            if sort.sort_by:
                order = desc(sort.sort_by) if sort.sort_order == "desc" else asc(sort.sort_by)
                query = query.order_by(order)
            return query.all()
    """

    def __init__(
        self,
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order


# ==================== Search Dependencies ====================

class SearchParams:
    """
    Search parameters for list endpoints.

    Usage:
        @router.get("/items")
        def search_items(search: SearchParams = Depends()):
            query = db.query(Item)
            if search.q:
                query = query.filter(Item.name.ilike(f"%{search.q}%"))
            return query.all()
    """

    def __init__(
        self,
        q: Optional[str] = Query(None, description="Search query"),
        fields: Optional[str] = Query(None, description="Comma-separated fields to search"),
    ):
        self.q = q
        self.fields = fields.split(",") if fields else []


# ==================== Filter Dependencies ====================

class DateRangeParams:
    """
    Date range filter parameters.

    Usage:
        @router.get("/itineraries")
        def list_itineraries(date_range: DateRangeParams = Depends()):
            query = db.query(Itinerary)
            if date_range.start_date:
                query = query.filter(Itinerary.start_date >= date_range.start_date)
            if date_range.end_date:
                query = query.filter(Itinerary.end_date <= date_range.end_date)
            return query.all()
    """

    def __init__(
        self,
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    ):
        self.start_date = start_date
        self.end_date = end_date


# ==================== Common Query Dependencies ====================

class CommonQueryParams:
    """
    Common query parameters combining pagination, sorting, and search.

    Usage:
        @router.get("/items")
        def list_items(
            common: CommonQueryParams = Depends(),
            db: Session = Depends(get_db)
        ):
            query = db.query(Item)

            # Apply search
            if common.q:
                query = query.filter(Item.name.ilike(f"%{common.q}%"))

            # Apply sorting
            if common.sort_by:
                order = desc(common.sort_by) if common.sort_order == "desc" else asc(common.sort_by)
                query = query.order_by(order)

            # Get total count
            total = query.count()

            # Apply pagination
            items = query.offset(common.skip).limit(common.limit).all()

            return {
                "items": items,
                "total": total,
                "page": common.page,
                "page_size": common.page_size,
                "total_pages": (total + common.page_size - 1) // common.page_size
            }
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
        q: Optional[str] = Query(None, description="Search query"),
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
        self.limit = page_size
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.q = q


# ==================== Validation Helpers ====================

def validate_id(id: int) -> int:
    """
    Validate that an ID is positive.

    Args:
        id: ID to validate

    Returns:
        int: Validated ID

    Raises:
        HTTPException: If ID is invalid
    """
    if id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID"
        )
    return id


def validate_exists(obj, obj_type: str = "Resource"):
    """
    Validate that an object exists.

    Args:
        obj: Object to validate
        obj_type: Type of object for error message

    Returns:
        The object if it exists

    Raises:
        HTTPException: If object doesn't exist
    """
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{obj_type} not found"
        )
    return obj


# ==================== Response Helpers ====================

def create_response(
    data: any,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
) -> dict:
    """
    Create a standardized API response.

    Args:
        data: Response data
        message: Response message
        status_code: HTTP status code

    Returns:
        dict: Standardized response
    """
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def create_error_response(
    message: str,
    details: Optional[dict] = None,
) -> dict:
    """
    Create a standardized error response.

    Args:
        message: Error message
        details: Optional error details

    Returns:
        dict: Standardized error response
    """
    response = {
        "success": False,
        "message": message,
    }
    if details:
        response["details"] = details
    return response


def create_paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
) -> dict:
    """
    Create a paginated response.

    Args:
        items: List of items
        total: Total count of items
        page: Current page number
        page_size: Items per page

    Returns:
        dict: Paginated response with metadata
    """
    total_pages = (total + page_size - 1) // page_size

    return {
        "success": True,
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    }
