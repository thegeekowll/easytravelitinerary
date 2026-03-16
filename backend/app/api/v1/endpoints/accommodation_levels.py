"""
Accommodation Level management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin
)
from app.models.accommodation import AccommodationLevel
from app.models.user import User
from app.schemas.accommodation import (
    AccommodationLevelCreate,
    AccommodationLevelResponse
)

router = APIRouter(prefix="/accommodation-levels", tags=["accommodation-levels"])


@router.get("", response_model=List[AccommodationLevelResponse])
async def list_accommodation_levels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all accommodation levels."""
    return db.query(AccommodationLevel).all()


@router.post("", response_model=AccommodationLevelResponse, status_code=status.HTTP_201_CREATED)
async def create_accommodation_level(
    level_data: AccommodationLevelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new accommodation level (admin only)."""
    existing = db.query(AccommodationLevel).filter(
        AccommodationLevel.name == level_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accommodation level already exists"
        )

    level = AccommodationLevel(**level_data.model_dump())
    db.add(level)
    db.commit()
    db.refresh(level)
    return level


@router.delete("/{level_id}", status_code=status.HTTP_200_OK)
async def delete_accommodation_level(
    level_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete an accommodation level (admin only)."""
    level = db.query(AccommodationLevel).filter(AccommodationLevel.id == level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accommodation level not found"
        )
        
    # Check if in use
    if level.accommodations.count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete level that is in use by accommodations"
        )
        
    db.delete(level)
    db.commit()
    return {"message": "Accommodation level deleted successfully"}
