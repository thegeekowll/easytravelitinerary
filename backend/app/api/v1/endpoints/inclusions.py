"""
Inclusion management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin
)
from app.models.inclusion_exclusion import Inclusion
from app.models.user import User
from app.schemas.inclusion import (
    InclusionCreate,
    InclusionUpdate,
    InclusionResponse
)

router = APIRouter(prefix="/inclusions", tags=["inclusions"])


@router.get("", response_model=List[InclusionResponse])
async def list_inclusions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all inclusions."""
    return db.query(Inclusion).order_by(Inclusion.sort_order).all()


@router.post("", response_model=InclusionResponse, status_code=status.HTTP_201_CREATED)
async def create_inclusion(
    inclusion_data: InclusionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new inclusion (admin only)."""
    existing = db.query(Inclusion).filter(Inclusion.name == inclusion_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inclusion with this name already exists"
        )

    inclusion = Inclusion(**inclusion_data.model_dump())
    db.add(inclusion)
    db.commit()
    db.refresh(inclusion)
    return inclusion


@router.delete("/{inclusion_id}", status_code=status.HTTP_200_OK)
async def delete_inclusion(
    inclusion_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete an inclusion (admin only)."""
    inclusion = db.query(Inclusion).filter(Inclusion.id == inclusion_id).first()
    if not inclusion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inclusion not found"
        )

    db.delete(inclusion)
    db.commit()
    return {"message": "Inclusion deleted successfully"}
