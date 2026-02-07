"""
Notification-related Pydantic schemas.

This module contains schemas for managing system notifications.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.notification import NotificationTypeEnum


class NotificationBase(BaseModel):
    """Base notification schema with common fields."""

    user_id: UUID = Field(
        ...,
        description="ID of the user this notification is for"
    )
    notification_type: NotificationTypeEnum = Field(
        ...,
        description="Type of notification"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Notification title/heading"
    )
    message: str = Field(
        ...,
        min_length=1,
        description="Notification message content"
    )
    related_itinerary_id: Optional[UUID] = Field(
        None,
        description="ID of related itinerary (if applicable)"
    )
    is_read: bool = Field(
        default=False,
        description="Whether the user has read this notification"
    )
    priority: Optional[str] = Field(
        default="normal",
        max_length=20,
        description="Notification priority (low, normal, high, urgent)"
    )

    model_config = ConfigDict(from_attributes=True)


class NotificationCreate(NotificationBase):
    """Schema for creating a new notification.

    Used by the system to generate notifications for users.
    """

    pass


class NotificationUpdate(BaseModel):
    """Schema for updating a notification.

    Typically used to mark notifications as read.
    """

    is_read: Optional[bool] = Field(
        None,
        description="Updated read status"
    )
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated title"
    )
    message: Optional[str] = Field(
        None,
        min_length=1,
        description="Updated message"
    )
    priority: Optional[str] = Field(
        None,
        max_length=20,
        description="Updated priority"
    )

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(NotificationBase):
    """Notification schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique notification identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the notification was created"
    )
    read_at: Optional[datetime] = Field(
        None,
        description="When the notification was marked as read"
    )

    model_config = ConfigDict(from_attributes=True)


class NotificationMarkAllRead(BaseModel):
    """Schema for marking all notifications as read for a user."""

    user_id: UUID = Field(
        ...,
        description="ID of the user whose notifications should be marked as read"
    )

    model_config = ConfigDict(from_attributes=True)


class NotificationSummary(BaseModel):
    """Summary of notifications for a user.

    Shows counts of unread notifications by type.
    """

    total_unread: int = Field(
        ...,
        description="Total number of unread notifications"
    )
    unread_by_type: dict[str, int] = Field(
        ...,
        description="Count of unread notifications by type"
    )
    latest_notification: Optional[NotificationResponse] = Field(
        None,
        description="Most recent notification"
    )

    model_config = ConfigDict(from_attributes=True)
