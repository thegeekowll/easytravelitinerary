"""
Celery async tasks.

This module contains all Celery tasks for background processing.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from celery import shared_task
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.email_service import email_service

from app.services.notification_service import notification_service
from app.models.email_log import EmailLog, DeliveryStatusEnum
from app.models.notification import Notification
from app.core.config import settings


def get_db() -> Session:
    """Get database session for Celery tasks."""
    return SessionLocal()


# ==================== Email Tasks ====================

@shared_task(name="app.services.celery_tasks.send_email_async", bind=True, max_retries=3)
def send_email_async(
    self,
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = None,
    from_name: str = None,
    attachments: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Send email asynchronously via SendGrid.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        from_email: Sender email (optional)
        from_name: Sender name (optional)
        attachments: List of attachments (optional)

    Returns:
        dict: Email send result with status
    """
    db = get_db()
    try:
        result = email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            from_email=from_email,
            from_name=from_name,
            attachments=attachments or [],
            db=db,
        )
        return {
            "success": True,
            "message": "Email sent successfully",
            "to_email": to_email,
            "subject": subject,
        }
    except Exception as exc:
        db.close()
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
    finally:
        db.close()


@shared_task(name="app.services.celery_tasks.send_itinerary_email")
def send_itinerary_email(
    itinerary_id: str,
    recipient_email: str,
) -> Dict[str, Any]:
    """
    Send itinerary email.

    Args:
        itinerary_id: Itinerary UUID
        recipient_email: Recipient email

    Returns:
        dict: Email send result
    """
    db = get_db()
    try:
        from app.models.itinerary import Itinerary

        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
        if not itinerary:
            return {"success": False, "error": "Itinerary not found"}

        # Send email
        subject = f"Your Itinerary: {itinerary.title}"
        html_content = f"""
        <html>
        <body>
            <h2>Your Travel Itinerary</h2>
            <p>Dear {itinerary.customer_name},</p>
            <p>Please find your itinerary details below.</p>
            <h3>{itinerary.title}</h3>
            <p><strong>Duration:</strong> {itinerary.duration_days} days / {itinerary.duration_nights} nights</p>
            <p><strong>Start Date:</strong> {itinerary.start_date}</p>
            <p>We look forward to serving you!</p>
            <br>
            <p>Best regards,<br>{settings.EMAIL_FROM_NAME}</p>
        </body>
        </html>
        """

        return send_email_async(
            to_email=recipient_email,
            subject=subject,
            html_content=html_content,
        )
    finally:
        db.close()





# ==================== Notification Tasks ====================

@shared_task(name="app.services.celery_tasks.check_upcoming_arrivals")
def check_upcoming_arrivals() -> Dict[str, Any]:
    """
    Check for itineraries with arrivals in 3 days and send notifications.

    This task runs daily at 9 AM.

    Returns:
        dict: Number of notifications sent
    """
    db = get_db()
    # We use run_until_complete because check_upcoming_arrivals is async
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        from app.services.notification_service import notification_service
        
        # Since this is a sync Celery task calling an async service method
        result = loop.run_until_complete(notification_service.check_upcoming_arrivals(db))
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        db.close()


@shared_task(name="app.services.celery_tasks.send_notification_email")
def send_notification_email(notification_id: str) -> Dict[str, Any]:
    """
    Send email for a notification.

    Args:
        notification_id: Notification UUID

    Returns:
        dict: Email send result
    """
    db = get_db()
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if not notification or not notification.user:
            return {"success": False, "error": "Notification or user not found"}

        html_content = f"""
        <html>
        <body>
            <h2>{notification.title}</h2>
            <p>{notification.message}</p>
            {f'<p><a href="{settings.FRONTEND_URL}{notification.action_url}">View Details</a></p>' if notification.action_url else ''}
            <br>
            <p>Best regards,<br>{settings.EMAIL_FROM_NAME}</p>
        </body>
        </html>
        """

        return send_email_async(
            to_email=notification.user.email,
            subject=notification.title,
            html_content=html_content,
        )
    finally:
        db.close()


# ==================== Cleanup Tasks ====================

@shared_task(name="app.services.celery_tasks.cleanup_old_notifications")
def cleanup_old_notifications(days: int = 90) -> Dict[str, Any]:
    """
    Delete read notifications older than specified days.

    Args:
        days: Number of days to keep notifications

    Returns:
        dict: Cleanup result
    """
    db = get_db()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted_count = db.query(Notification).filter(
            Notification.is_read == True,
            Notification.created_at < cutoff_date,
        ).delete()

        db.commit()

        return {
            "success": True,
            "deleted_count": deleted_count,
            "cutoff_date": str(cutoff_date),
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task(name="app.services.celery_tasks.cleanup_old_email_logs")
def cleanup_old_email_logs(days: int = 180) -> Dict[str, Any]:
    """
    Delete old email logs.

    Args:
        days: Number of days to keep email logs

    Returns:
        dict: Cleanup result
    """
    db = get_db()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted_count = db.query(EmailLog).filter(
            EmailLog.sent_at < cutoff_date,
            EmailLog.status == DeliveryStatusEnum.DELIVERED,
        ).delete()

        db.commit()

        return {
            "success": True,
            "deleted_count": deleted_count,
            "cutoff_date": str(cutoff_date),
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


# ==================== Analytics Tasks ====================

@shared_task(name="app.services.celery_tasks.generate_daily_analytics")
def generate_daily_analytics() -> Dict[str, Any]:
    """
    Generate daily analytics summary.

    Returns:
        dict: Analytics result
    """
    db = get_db()
    try:
        from app.models.itinerary import Itinerary
        from app.models.user import User
        from datetime import date

        today = date.today()

        # Count new itineraries created today
        new_itineraries = db.query(Itinerary).filter(
            Itinerary.created_at >= datetime.combine(today, datetime.min.time())
        ).count()

        # Count active users today
        active_users = db.query(User).filter(
            User.last_login >= datetime.combine(today, datetime.min.time())
        ).count()

        return {
            "success": True,
            "date": str(today),
            "new_itineraries": new_itineraries,
            "active_users": active_users,
        }
    finally:
        db.close()
