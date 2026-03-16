from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.v1.deps import get_db, require_permission
from app.models.base_tour import TourType
from app.schemas.base_tour import TourTypeResponse

router = APIRouter()

@router.get("", response_model=List[TourTypeResponse])
def get_tour_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve tour types.
    """
    stmt = select(TourType).offset(skip).limit(limit)
    return db.scalars(stmt).all()
