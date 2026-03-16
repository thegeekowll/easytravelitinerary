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
        # Itinerary
        {"name": PermissionNames.CREATE_ITINERARY, "description": "Create new itineraries", "category": PermissionCategories.ITINERARY},
        {"name": PermissionNames.EDIT_ITINERARY, "description": "Edit existing itineraries", "category": PermissionCategories.ITINERARY},
        {"name": PermissionNames.DELETE_ITINERARY, "description": "Delete itineraries", "category": PermissionCategories.ITINERARY},
        {"name": PermissionNames.VIEW_ALL_ITINERARIES, "description": "View all agents' itineraries (not just own)", "category": PermissionCategories.ITINERARY},
        {"name": PermissionNames.SEND_ITINERARY_EMAIL, "description": "Send itinerary emails to travelers", "category": PermissionCategories.ITINERARY},
        {"name": PermissionNames.GENERATE_ITINERARY_PDF, "description": "Generate and download PDF itineraries", "category": PermissionCategories.ITINERARY},

        # Destination
        {"name": PermissionNames.VIEW_DESTINATIONS, "description": "View the destinations list", "category": PermissionCategories.DESTINATION},
        {"name": PermissionNames.ADD_DESTINATION, "description": "Add new destinations", "category": PermissionCategories.DESTINATION},
        {"name": PermissionNames.EDIT_DESTINATION, "description": "Edit existing destinations", "category": PermissionCategories.DESTINATION},
        {"name": PermissionNames.DELETE_DESTINATION, "description": "Delete destinations", "category": PermissionCategories.DESTINATION},

        # Accommodation
        {"name": PermissionNames.VIEW_ACCOMMODATIONS, "description": "View the accommodations list", "category": PermissionCategories.ACCOMMODATION},
        {"name": PermissionNames.ADD_ACCOMMODATION, "description": "Add new accommodations", "category": PermissionCategories.ACCOMMODATION},
        {"name": PermissionNames.EDIT_ACCOMMODATION, "description": "Edit existing accommodations", "category": PermissionCategories.ACCOMMODATION},
        {"name": PermissionNames.DELETE_ACCOMMODATION, "description": "Delete accommodations", "category": PermissionCategories.ACCOMMODATION},

        # Base Tours
        {"name": PermissionNames.VIEW_TOUR_PACKAGES, "description": "View base tour templates", "category": PermissionCategories.TOUR_PACKAGE},
        {"name": PermissionNames.ADD_TOUR_PACKAGE, "description": "Create new base tours", "category": PermissionCategories.TOUR_PACKAGE},
        {"name": PermissionNames.EDIT_TOUR_PACKAGE, "description": "Edit existing base tours", "category": PermissionCategories.TOUR_PACKAGE},
        {"name": PermissionNames.DELETE_TOUR_PACKAGE, "description": "Delete base tours", "category": PermissionCategories.TOUR_PACKAGE},

        # 2D Matrix
        {"name": PermissionNames.VIEW_2D_TABLE, "description": "View the destination combination matrix", "category": PermissionCategories.TWO_D_TABLE},
        {"name": PermissionNames.EDIT_2D_TABLE, "description": "Edit matrix combinations", "category": PermissionCategories.TWO_D_TABLE},

        # Analytics
        {"name": PermissionNames.VIEW_ANALYTICS, "description": "View analytics dashboard", "category": PermissionCategories.ANALYTICS},
        {"name": PermissionNames.VIEW_ANALYTICS_REVENUE, "description": "View revenue and financial analytics", "category": PermissionCategories.ANALYTICS},
        {"name": PermissionNames.EXPORT_ANALYTICS, "description": "Export analytics reports", "category": PermissionCategories.ANALYTICS},

        # User Management
        {"name": PermissionNames.VIEW_USERS, "description": "View the users list", "category": PermissionCategories.USER_MANAGEMENT},
        {"name": PermissionNames.MANAGE_USERS, "description": "Create, edit, and delete users", "category": PermissionCategories.USER_MANAGEMENT},

        # System / Settings
        {"name": PermissionNames.MANAGE_AGENT_TYPES, "description": "Manage company settings, branding, and configuration", "category": PermissionCategories.SYSTEM},
        {"name": PermissionNames.VIEW_ACTIVITY_LOGS, "description": "View system activity logs", "category": PermissionCategories.SYSTEM},
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
