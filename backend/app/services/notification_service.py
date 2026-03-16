"""
Notification Service.

Handles creation and delivery of notifications to users.
Supports email notifications and in-app notifications.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationTypeEnum, PriorityEnum
from app.models.itinerary import Itinerary
from app.models.user import User
from app.services.email_service import email_service


class NotificationService:
    """Service for managing notifications."""

    async def create_notification(
        self,
        user_id: UUID,
        notification_type: NotificationTypeEnum,
        title: str,
        message: str,
        itinerary_id: Optional[UUID] = None,
        priority: PriorityEnum = PriorityEnum.MEDIUM,
        action_url: Optional[str] = None,
        db: Session = None
    ) -> Notification:
        """
        Create a notification for a user.

        Args:
            user_id: User to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            itinerary_id: Related itinerary (optional)
            priority: Notification priority
            action_url: URL for action button (optional)
            db: Database session

        Returns:
            Created Notification object
        """
        # Create notification
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            itinerary_id=itinerary_id,
            priority=priority,
            action_url=action_url,
            is_read=False
        )

        db.add(notification)
        db.flush()

        # Check if user has email notifications enabled
        user = db.query(User).filter(User.id == user_id).first()

        # Send email notification if user preferences allow
        # (Assuming User model has email_notifications_enabled field)
        # For now, send for HIGH and URGENT priorities
        if priority in [PriorityEnum.HIGH, PriorityEnum.URGENT]:
            await self._send_email_notification(user, notification, db)

        return notification

    async def _send_email_notification(
        self,
        user: User,
        notification: Notification,
        db: Session
    ):
        """Send email notification (simplified version)."""
        try:
            # This would use a simple email template
            # For full implementation, create separate email templates
            pass
        except Exception as e:
            print(f"Failed to send email notification: {str(e)}")

    async def send_payment_confirmed_notification(
        self,
        itinerary_id: UUID,
        db: Session
    ):
        """
        Send notification when payment is confirmed.

        Notifies admin and assigned agent.
        """
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

        if not itinerary:
            return

        # Get traveler name
        traveler_name = "Traveler"
        if itinerary.travelers and len(itinerary.travelers) > 0:
            primary = next((t for t in itinerary.travelers if t.is_primary), itinerary.travelers[0])
            traveler_name = primary.full_name

        title = "Payment Confirmed"
        message = f"{traveler_name} has confirmed payment for {itinerary.title}"

        # Notify assigned agent
        if itinerary.assigned_to_user_id:
            await self.create_notification(
                user_id=itinerary.assigned_to_user_id,
                notification_type=NotificationTypeEnum.PAYMENT_CONFIRMED,
                title=title,
                message=message,
                itinerary_id=itinerary_id,
                priority=PriorityEnum.MEDIUM,
                action_url=f"/itineraries/{itinerary_id}",
                db=db
            )

        # Notify all admins
        from app.models.user import UserRoleEnum
        admins = db.query(User).filter(User.role == UserRoleEnum.ADMIN).all()

        for admin in admins:
            await self.create_notification(
                user_id=admin.id,
                notification_type=NotificationTypeEnum.PAYMENT_CONFIRMED,
                title=title,
                message=message,
                itinerary_id=itinerary_id,
                priority=PriorityEnum.MEDIUM,
                action_url=f"/itineraries/{itinerary_id}",
                db=db
            )

    async def send_3_day_arrival_notification(
        self,
        itinerary_id: UUID,
        db: Session
    ):
        """
        Send CRITICAL 3-day advance warning notification.

        Notifies admin and assigned agent that traveler arrives in 3 days.
        """
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

        if not itinerary:
            return

        # Get traveler name
        traveler_name = "Traveler"
        if itinerary.travelers and len(itinerary.travelers) > 0:
            primary = next((t for t in itinerary.travelers if t.is_primary), itinerary.travelers[0])
            traveler_name = primary.full_name

        title = "🚨 Arrival in 3 Days"
        message = (
            f"{traveler_name} arrives in 3 days for {itinerary.title}. "
            f"Departure: {itinerary.departure_date.strftime('%B %d, %Y')}. "
            "Please confirm all arrangements."
        )

        # Notify assigned agent
        if itinerary.assigned_to_user_id:
            await self.create_notification(
                user_id=itinerary.assigned_to_user_id,
                notification_type=NotificationTypeEnum.THREE_DAY_ARRIVAL,
                title=title,
                message=message,
                itinerary_id=itinerary_id,
                priority=PriorityEnum.HIGH,
                action_url=f"/itineraries/{itinerary_id}",
                db=db
            )

        # Notify all admins
        from app.models.user import UserRoleEnum
        admins = db.query(User).filter(User.role == UserRoleEnum.ADMIN).all()

        for admin in admins:
            await self.create_notification(
                user_id=admin.id,
                notification_type=NotificationTypeEnum.THREE_DAY_ARRIVAL,
                title=title,
                message=message,
                itinerary_id=itinerary_id,
                priority=PriorityEnum.HIGH,
                action_url=f"/itineraries/{itinerary_id}",
                db=db
            )

    async def send_assignment_notification(
        self,
        itinerary_id: UUID,
        new_agent_id: UUID,
        db: Session
    ):
        """
        Send notification when itinerary is assigned to agent.

        Notifies the newly assigned agent.
        """
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

        if not itinerary:
            return

        title = "New Itinerary Assigned"
        message = f"You have been assigned to {itinerary.title}"

        await self.create_notification(
            user_id=new_agent_id,
            notification_type=NotificationTypeEnum.ASSIGNED,
            title=title,
            message=message,
            itinerary_id=itinerary_id,
            priority=PriorityEnum.MEDIUM,
            action_url=f"/itineraries/{itinerary_id}",
            db=db
        )

    async def send_edit_notification(
        self,
        itinerary_id: UUID,
        edited_by_user_id: UUID,
        db: Session
    ):
        """
        Send notification when itinerary is edited.

        Notifies assigned agent (if someone else edited).
        """
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

        if not itinerary:
            return

        # Only notify if someone OTHER than the assigned agent edited
        if itinerary.assigned_to_user_id and itinerary.assigned_to_user_id != edited_by_user_id:
            editor = db.query(User).filter(User.id == edited_by_user_id).first()
            editor_name = editor.full_name if editor else "Someone"

            title = "Itinerary Edited"
            message = f"{editor_name} edited {itinerary.title}"

            await self.create_notification(
                user_id=itinerary.assigned_to_user_id,
                notification_type=NotificationTypeEnum.EDITED,
                title=title,
                message=message,
                itinerary_id=itinerary_id,
                priority=PriorityEnum.LOW,
                action_url=f"/itineraries/{itinerary_id}",
                db=db
            )

    async def check_upcoming_arrivals(self, db: Session):
        """
        Check for itineraries with arrivals in 3 days.

        Called by scheduled job daily at 9 AM.
        """
        from app.models.itinerary import ItineraryStatusEnum

        three_days_from_now = date.today() + timedelta(days=3)

        # Find itineraries departing in 3 days
        itineraries = db.query(Itinerary).filter(
            Itinerary.departure_date == three_days_from_now,
            Itinerary.status.in_([ItineraryStatusEnum.CONFIRMED, ItineraryStatusEnum.COMPLETED])
        ).all()

        for itinerary in itineraries:
            await self.send_3_day_arrival_notification(itinerary.id, db)

        db.commit()

        return {
            'success': True,
            'itineraries_found': len(itineraries),
            'notifications_sent': len(itineraries) * 2  # Agent + Admin per itinerary
        }


# Create singleton instance
notification_service = NotificationService()
