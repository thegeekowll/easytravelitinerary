from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.v1.deps import get_db, require_admin
from app.models.user import User
from app.models.permission import Permission, PermissionNames, PermissionCategories
from app.schemas.permission import PermissionResponse

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.get("", response_model=List[PermissionResponse])
async def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all available permissions.
    """
    permissions = db.query(Permission).all()
    return permissions

@router.post("/seed", response_model=Dict[str, int])
async def seed_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Seed default permissions if they don't exist.
    """
    # Define default permissions
    default_permissions = [
        # Accommodation
        {"name": PermissionNames.VIEW_ACCOMMODATIONS, "description": "View accommodations", "category": PermissionCategories.ACCOMMODATION},
        {"name": PermissionNames.ADD_ACCOMMODATION, "description": "Add new accommodations", "category": PermissionCategories.ACCOMMODATION},
        {"name": PermissionNames.EDIT_ACCOMMODATION, "description": "Edit existing accommodations", "category": PermissionCategories.ACCOMMODATION},
        {"name": PermissionNames.DELETE_ACCOMMODATION, "description": "Delete accommodations", "category": PermissionCategories.ACCOMMODATION},
        
        # Destination
        {"name": PermissionNames.VIEW_DESTINATIONS, "description": "View destinations", "category": PermissionCategories.DESTINATION},
        {"name": PermissionNames.ADD_DESTINATION, "description": "Add new destinations", "category": PermissionCategories.DESTINATION},
        {"name": PermissionNames.EDIT_DESTINATION, "description": "Edit existing destinations", "category": PermissionCategories.DESTINATION},
        {"name": PermissionNames.DELETE_DESTINATION, "description": "Delete destinations", "category": PermissionCategories.DESTINATION},
        
        # Base Tours
        {"name": PermissionNames.VIEW_TOUR_PACKAGES, "description": "View base tours", "category": PermissionCategories.TOUR_PACKAGE},
        {"name": PermissionNames.ADD_TOUR_PACKAGE, "description": "Add new base tours", "category": PermissionCategories.TOUR_PACKAGE},
        {"name": PermissionNames.EDIT_TOUR_PACKAGE, "description": "Edit existing base tours", "category": PermissionCategories.TOUR_PACKAGE},
        {"name": PermissionNames.DELETE_TOUR_PACKAGE, "description": "Delete base tours", "category": PermissionCategories.TOUR_PACKAGE},
        
        # 2D Table
        {"name": PermissionNames.VIEW_2D_TABLE, "description": "View 2D Matrix", "category": PermissionCategories.TWO_D_TABLE},
        {"name": PermissionNames.EDIT_2D_TABLE, "description": "Edit 2D Matrix", "category": PermissionCategories.TWO_D_TABLE},
        
        # Settings (System)
        {"name": PermissionNames.MANAGE_AGENT_TYPES, "description": "Manage Settings & Configurations", "category": PermissionCategories.SYSTEM},
    ]

    added_count = 0
    for perm_data in default_permissions:
        stmt = select(Permission).where(Permission.name == perm_data["name"])
        existing = db.execute(stmt).scalar_one_or_none()
        
        if not existing:
            new_perm = Permission(
                name=perm_data["name"],
                description=perm_data["description"],
                category=perm_data["category"]
            )
            db.add(new_perm)
            added_count += 1
    
    db.commit()
    
    return {"added": added_count, "total": len(default_permissions)}
