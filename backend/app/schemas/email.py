"""
Email-related Pydantic schemas.

This module contains schemas for sending emails and logging email records.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from app.models.email_log import DeliveryStatusEnum


class EmailSendRequest(BaseModel):
    """Schema for sending an email.

    Used when agents want to send itineraries or other communications to clients.
    """

    to_email: EmailStr = Field(
        ...,
        description="Recipient email address"
    )
    to_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Recipient name"
    )
    subject: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Email subject line"
    )
    body_html: Optional[str] = Field(
        None,
        description="HTML version of email body"
    )
    body_text: str = Field(
        ...,
        description="Plain text version of email body (required as fallback)"
    )
    itinerary_id: Optional[UUID] = Field(
        None,
        description="ID of the itinerary being sent (if applicable)"
    )
    cc_emails: Optional[List[EmailStr]] = Field(
        default=None,
        description="List of CC email addresses"
    )
    bcc_emails: Optional[List[EmailStr]] = Field(
        default=None,
        description="List of BCC email addresses"
    )
    attachments: Optional[List[str]] = Field(
        default=None,
        description="List of attachment URLs or file paths"
    )
    reply_to: Optional[EmailStr] = Field(
        None,
        description="Reply-to email address (defaults to sender)"
    )
    template_id: Optional[str] = Field(
        None,
        max_length=100,
        description="SendGrid template ID (if using templates)"
    )
    template_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Dynamic data for email template"
    )

    model_config = ConfigDict(from_attributes=True)


class EmailLogResponse(BaseModel):
    """Email log schema for API responses.

    Records all emails sent from the system for audit purposes.
    """

    id: UUID = Field(
        ...,
        description="Unique email log identifier"
    )
    itinerary_id: Optional[UUID] = Field(
        None,
        description="ID of related itinerary (if applicable)"
    )
    sent_by_user_id: Optional[UUID] = Field(
        None,
        description="ID of the user who sent the email"
    )
    recipient_email: EmailStr = Field(
        ...,
        description="Recipient email address"
    )
    recipient_name: Optional[str] = Field(
        None,
        description="Recipient name"
    )
    subject: str = Field(
        ...,
        description="Email subject line"
    )
    email_type: Optional[str] = Field(
        None,
        description="Type/category of email"
    )
    status: DeliveryStatusEnum = Field(
        ...,
        description="Email delivery status"
    )
    sent_at: Optional[datetime] = Field(
        None,
        description="When the email was successfully sent"
    )
    opened_at: Optional[datetime] = Field(
        None,
        description="When the email was first opened (if tracking enabled)"
    )
    clicked_at: Optional[datetime] = Field(
        None,
        description="When a link in the email was first clicked (if tracking enabled)"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if email failed to send"
    )
    sendgrid_message_id: Optional[str] = Field(
        None,
        description="SendGrid message ID for tracking"
    )
    created_at: datetime = Field(
        ...,
        description="When the email log was created"
    )

    model_config = ConfigDict(from_attributes=True)


class EmailBulkSendRequest(BaseModel):
    """Schema for sending bulk emails.

    Used for sending the same email to multiple recipients.
    """

    recipients: List[EmailStr] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of recipient email addresses (max 100 per batch)"
    )
    subject: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Email subject line"
    )
    body_html: Optional[str] = Field(
        None,
        description="HTML version of email body"
    )
    body_text: str = Field(
        ...,
        description="Plain text version of email body"
    )
    template_id: Optional[str] = Field(
        None,
        max_length=100,
        description="SendGrid template ID"
    )

    model_config = ConfigDict(from_attributes=True)


class EmailStatistics(BaseModel):
    """Email statistics for an itinerary.

    Shows email engagement metrics.
    """

    total_sent: int = Field(
        ...,
        description="Total emails sent for this itinerary"
    )
    total_delivered: int = Field(
        ...,
        description="Total emails successfully delivered"
    )
    total_opened: int = Field(
        ...,
        description="Total emails opened"
    )
    total_clicked: int = Field(
        ...,
        description="Total emails with link clicks"
    )
    total_failed: int = Field(
        ...,
        description="Total emails that failed to send"
    )
    last_sent_at: Optional[datetime] = Field(
        None,
        description="When the most recent email was sent"
    )

    model_config = ConfigDict(from_attributes=True)
