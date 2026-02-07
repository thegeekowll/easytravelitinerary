"""
Dashboard endpoints.

Provides analytics and statistics for agent and admin dashboards.
"""
from datetime import date, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_active_user, require_admin
from app.models.user import User
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/agent-stats")
async def get_agent_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get real-time stats for agent dashboard."""
    stats = analytics_service.get_agent_stats(current_user.id, db)
    return stats


@router.get("/agent-analytics")
async def get_agent_analytics(
    agent_id: UUID = Query(None, description="Agent ID (admin only, or leave empty for self)"),
    date_from: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    date_to: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get historical analytics for an agent."""
    from app.models.user import UserRoleEnum

    # If agent_id not provided, use current user
    target_user_id = agent_id if agent_id else current_user.id

    # Only admins can view other agents' analytics
    if target_user_id != current_user.id and current_user.role != UserRoleEnum.ADMIN:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other agents' analytics"
        )

    analytics = analytics_service.get_agent_analytics(target_user_id, date_from, date_to, db)
    return analytics


@router.get("/admin-stats")
async def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get real-time stats for admin dashboard (admin only)."""
    stats = analytics_service.get_admin_stats(db)
    return stats


@router.get("/company-analytics")
async def get_company_analytics(
    date_from: date = Query(default_factory=lambda: date.today() - timedelta(days=90)),
    date_to: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get company-wide analytics (admin only)."""
    analytics = analytics_service.get_company_analytics(date_from, date_to, db)
    return analytics
