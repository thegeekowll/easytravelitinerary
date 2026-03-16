"""
Notification endpoints.

Manage user notifications.
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
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=PaginatedResponse[dict])
async def list_notifications(
    pagination: PaginationParams = Depends(),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List current user's notifications with pagination."""
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    if notification_type and notification_type != 'all':
        # Simple string matching assuming frontend passes valid enum values
        query = query.filter(Notification.notification_type == notification_type)

    if priority and priority != 'all':
        query = query.filter(Notification.priority == priority)

    total = query.count()

    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(pagination.skip).limit(pagination.limit).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=[
            {
                'id': str(n.id),
                'type': n.notification_type.value,
                'title': n.title,
                'message': n.message,
                'priority': n.priority.value,
                'is_read': n.is_read,
                'action_url': n.action_url,
                'itinerary_id': str(n.itinerary_id) if n.itinerary_id else None,
                'created_at': n.created_at.isoformat()
            }
            for n in notifications
        ],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )


@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get count of unread notifications."""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {'unread_count': count}


@router.patch("/{notification_id}/read", response_model=MessageResponse)
async def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.is_read = True
    db.commit()

    return MessageResponse(message="Notification marked as read")


@router.patch("/mark-all-read", response_model=MessageResponse)
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({'is_read': True})

    db.commit()

    return MessageResponse(message="All notifications marked as read")


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a notification."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return MessageResponse(message="Notification deleted")


@router.post("/send-custom", response_model=MessageResponse)
async def send_custom_notification(
    notification_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Send custom notification (admin only).

    Body: {
        "user_id": "uuid",
        "title": "Notification Title",
        "message": "Notification message",
        "priority": "medium",
        "action_url": "/path" (optional)
    }
    """
    from app.models.notification import NotificationTypeEnum, PriorityEnum

    await notification_service.create_notification(
        user_id=UUID(notification_data['user_id']),
        notification_type=NotificationTypeEnum.CUSTOM,
        title=notification_data['title'],
        message=notification_data['message'],
        priority=PriorityEnum(notification_data.get('priority', 'medium')),
        action_url=notification_data.get('action_url'),
        db=db
    )

    db.commit()

    return MessageResponse(message="Notification sent successfully")


@router.post("/trigger-checks", response_model=dict)
async def trigger_notification_checks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Manually trigger system notification checks (e.g. 3-day arrivals).
    Admin only.
    """
    from app.services.notification_service import notification_service
    
    result = await notification_service.check_upcoming_arrivals(db)
    return result
