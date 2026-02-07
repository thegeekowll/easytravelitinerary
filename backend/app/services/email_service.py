"""
Email Service.

Sends itineraries and notifications via SendGrid.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from app.models.itinerary import Itinerary
from app.models.email_log import EmailLog, DeliveryStatusEnum
from app.models.company import CompanyContent
from app.models.user import User
from app.core.config import settings



class EmailService:
    """Service for sending emails via SendGrid."""

    def __init__(self):
        """Initialize email service with Jinja2 templates."""
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )

    async def send_itinerary_email(
        self,
        itinerary_id: UUID,
        to_email: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        sent_by_user_id: UUID = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Send itinerary email to traveler.

        Args:
            itinerary_id: Itinerary to send
            to_email: Primary recipient
            cc: CC recipients
            bcc: BCC recipients
            subject: Email subject (uses template if not provided)
            body: Email body (uses template if not provided)
            sent_by_user_id: User who sent the email
            db: Database session

        Returns:
            Dict with success status and message
        """
        # Fetch itinerary
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

        if not itinerary:
            raise ValueError(f"Itinerary {itinerary_id} not found")

        # Get company content for templates
        company_content = db.query(CompanyContent).first()

        # Get primary traveler for personalization
        primary_traveler = None
        for traveler in itinerary.travelers:
            if traveler.is_primary:
                primary_traveler = traveler
                break

        if not primary_traveler and len(itinerary.travelers) > 0:
            primary_traveler = itinerary.travelers[0]

        # Get sender info
        sender = None
        if sent_by_user_id:
            sender = db.query(User).filter(User.id == sent_by_user_id).first()

        # Prepare email data
        email_data = {
            'traveler_name': primary_traveler.full_name if primary_traveler else 'Valued Traveler',
            'tour_name': itinerary.title,
            'tour_code': itinerary.unique_code,
            'departure_date': itinerary.departure_date.strftime('%B %d, %Y'),
            'web_link': f"{settings.FRONTEND_URL}/view/{itinerary.unique_code}",
            'agent_name': sender.full_name if sender else 'Travel Agency Team',
            'agent_email': sender.email if sender else settings.EMAILS_FROM_EMAIL,
            'agent_phone': sender.phone_number if sender else ''
        }

        # Use template or provided content
        if not subject:
            subject = f"Your {itinerary.title} Itinerary - {itinerary.unique_code}"

        if not body:
            # Use email template from CompanyContent
            if company_content and company_content.email_template:
                body = self._replace_placeholders(company_content.email_template, email_data)
            else:
                # Default template
                body = self._get_default_email_body(email_data)

        # Send email via SendGrid
        try:
            success = await self._send_via_sendgrid(
                to_email=to_email,
                cc=cc or [],
                bcc=bcc or [],
                subject=subject,
                body=body
            )

            delivery_status = DeliveryStatusEnum.SENT if success else DeliveryStatusEnum.FAILED

        except Exception as e:
            success = False
            delivery_status = DeliveryStatusEnum.FAILED
            print(f"Email send failed: {str(e)}")

        # Log email
        email_log = EmailLog(
            itinerary_id=itinerary_id,
            sent_to_email=to_email,
            cc_emails=cc or [],
            bcc_emails=bcc or [],
            subject=subject,
            body=body,
            delivery_status=delivery_status,
            sent_by_user_id=sent_by_user_id,
            sent_at=datetime.utcnow() if success else None,
            pdf_attached=False
        )

        db.add(email_log)

        # Update itinerary sent_at if first successful send
        if success and not itinerary.sent_at:
            itinerary.sent_at = datetime.utcnow()

        db.commit()

        return {
            'success': success,
            'message': 'Email sent successfully' if success else 'Email send failed',
            'email_id': str(email_log.id)
        }

    def _replace_placeholders(self, template: str, data: Dict[str, Any]) -> str:
        """Replace placeholders in email template."""
        result = template
        for key, value in data.items():
            placeholder = f"[{key.replace('_', ' ').title()}]"
            result = result.replace(placeholder, str(value))

        return result

    def _get_default_email_body(self, data: Dict[str, Any]) -> str:
        """Get default email body template."""
        return f"""
Dear {data['traveler_name']},

Your travel itinerary is ready! We're excited to share the details of your upcoming adventure: {data['tour_name']}.

🗓️ Departure Date: {data['departure_date']}
📋 Tour Code: {data['tour_code']}

VIEW YOUR ITINERARY:
You can view and download your complete itinerary online at:
{data['web_link']}

This link will remain active and can be shared with your travel companions.

WHAT'S INCLUDED:
✓ Detailed day-by-day itinerary
✓ Accommodation information
✓ Activity descriptions
✓ What's included & excluded
✓ Emergency contact information

If you have any questions or need to make changes, please don't hesitate to reach out.

Safe travels!

{data['agent_name']}
{data['agent_email']}
{data['agent_phone']}

---
This is an automated message from our Travel Management System.
"""

    async def _send_via_sendgrid(
        self,
        to_email: str,
        cc: List[str],
        bcc: List[str],
        subject: str,
        body: str
    ) -> bool:
        """
        Send email via SendGrid API.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            import requests

            if not settings.SENDGRID_API_KEY:
                print("SendGrid API key not configured. Email not sent (development mode).")
                return True  # Simulate success in development

            # Create email message
            message = Mail(
                from_email=settings.EMAILS_FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=body
            )

            # Add CC
            if cc:
                message.cc = cc

            # Add BCC
            if bcc:
                message.bcc = bcc

            # Send email
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)

            return response.status_code in [200, 201, 202]

        except ImportError:
            print("SendGrid not installed. Run: pip install sendgrid")
            return False

        except Exception as e:
            print(f"SendGrid send error: {str(e)}")
            return False

    async def resend_last_email(
        self,
        itinerary_id: UUID,
        db: Session
    ) -> Dict[str, Any]:
        """
        Resend the last email sent for an itinerary.

        Args:
            itinerary_id: Itinerary ID
            db: Database session

        Returns:
            Dict with success status and message
        """
        # Get last email
        last_email = db.query(EmailLog).filter(
            EmailLog.itinerary_id == itinerary_id
        ).order_by(EmailLog.sent_at.desc()).first()

        if not last_email:
            return {
                'success': False,
                'message': 'No previous email found'
            }

        # Resend with same parameters
        return await self.send_itinerary_email(
            itinerary_id=itinerary_id,
            to_email=last_email.sent_to_email,
            cc=last_email.cc_emails,
            bcc=last_email.bcc_emails,
            subject=last_email.subject,
            body=last_email.body,
            sent_by_user_id=last_email.sent_by_user_id,
            db=db
        )

    def get_email_history(
        self,
        itinerary_id: UUID,
        db: Session
    ) -> List[EmailLog]:
        """
        Get all emails sent for an itinerary.

        Args:
            itinerary_id: Itinerary ID
            db: Database session

        Returns:
            List of EmailLog objects
        """
        emails = db.query(EmailLog).filter(
            EmailLog.itinerary_id == itinerary_id
        ).order_by(EmailLog.sent_at.desc()).all()

        return emails


# Create singleton instance
email_service = EmailService()
