"""
Exclusion management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin
)
from app.models.inclusion_exclusion import Exclusion
from app.models.user import User
from app.schemas.exclusion import (
    ExclusionCreate,
    ExclusionUpdate,
    ExclusionResponse
)

router = APIRouter(prefix="/exclusions", tags=["exclusions"])


@router.get("", response_model=List[ExclusionResponse])
async def list_exclusions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all exclusions."""
    return db.query(Exclusion).order_by(Exclusion.sort_order).all()


@router.post("", response_model=ExclusionResponse, status_code=status.HTTP_201_CREATED)
async def create_exclusion(
    exclusion_data: ExclusionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new exclusion (admin only)."""
    existing = db.query(Exclusion).filter(Exclusion.name == exclusion_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exclusion with this name already exists"
        )

    exclusion = Exclusion(**exclusion_data.model_dump())
    db.add(exclusion)
    db.commit()
    db.refresh(exclusion)
    return exclusion


@router.delete("/{exclusion_id}", status_code=status.HTTP_200_OK)
async def delete_exclusion(
    exclusion_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete an exclusion (admin only)."""
    exclusion = db.query(Exclusion).filter(Exclusion.id == exclusion_id).first()
    if not exclusion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exclusion not found"
        )

    db.delete(exclusion)
    db.commit()
    return {"message": "Exclusion deleted successfully"}
