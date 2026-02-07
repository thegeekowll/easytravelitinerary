"""
Payment-related Pydantic schemas.

This module contains schemas for managing payment records and transactions.
"""
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.payment import PaymentStatusEnum


class PaymentRecordBase(BaseModel):
    """Base payment record schema with common fields."""

    itinerary_id: UUID = Field(
        ...,
        description="ID of the itinerary this payment is for"
    )
    amount: Decimal = Field(
        ...,
        description="Payment amount",
        gt=0,
        max_digits=10,
        decimal_places=2
    )
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)"
    )
    payment_method: Optional[str] = Field(
        None,
        max_length=100,
        description="Payment method used (e.g., 'credit_card', 'bank_transfer')"
    )
    payment_status: PaymentStatusEnum = Field(
        default=PaymentStatusEnum.NOT_PAID,
        description="Current payment status"
    )
    payment_date: Optional[date] = Field(
        None,
        description="Date when payment was made (null if pending)"
    )
    transaction_id: Optional[str] = Field(
        None,
        max_length=255,
        description="External transaction ID from payment processor"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about this payment"
    )

    @field_validator('currency')
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        """Validate currency code is uppercase and 3 characters."""
        v = v.upper()
        if len(v) != 3:
            raise ValueError('Currency code must be exactly 3 characters')
        if not v.isalpha():
            raise ValueError('Currency code must contain only letters')
        return v

    model_config = ConfigDict(from_attributes=True)


class PaymentRecordCreate(PaymentRecordBase):
    """Schema for creating a new payment record."""

    pass


class PaymentRecordUpdate(BaseModel):
    """Schema for updating an existing payment record.

    All fields are optional to support partial updates.
    Common use case: updating status from pending to completed.
    """

    amount: Optional[Decimal] = Field(
        None,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Updated payment amount"
    )
    currency: Optional[str] = Field(
        None,
        min_length=3,
        max_length=3,
        description="Updated currency code"
    )
    payment_method: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated payment method"
    )
    payment_status: Optional[PaymentStatusEnum] = Field(
        None,
        description="Updated payment status"
    )
    payment_date: Optional[date] = Field(
        None,
        description="Updated payment date"
    )
    transaction_id: Optional[str] = Field(
        None,
        max_length=255,
        description="Updated transaction ID"
    )
    notes: Optional[str] = Field(
        None,
        description="Updated notes"
    )

    @field_validator('currency')
    @classmethod
    def validate_currency_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate currency code is uppercase and 3 characters."""
        if v is None:
            return v
        v = v.upper()
        if len(v) != 3:
            raise ValueError('Currency code must be exactly 3 characters')
        if not v.isalpha():
            raise ValueError('Currency code must contain only letters')
        return v

    model_config = ConfigDict(from_attributes=True)


class PaymentRecordResponse(PaymentRecordBase):
    """Payment record schema for API responses."""

    id: UUID = Field(
        ...,
        description="Unique payment record identifier"
    )
    created_at: datetime = Field(
        ...,
        description="When the payment record was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the payment record was last updated"
    )

    model_config = ConfigDict(from_attributes=True)


class PaymentSummary(BaseModel):
    """Summary of payments for an itinerary.

    Used to show total amounts paid, pending, and refunded.
    """

    total_paid: Decimal = Field(
        ...,
        description="Total amount paid (completed payments)"
    )
    total_pending: Decimal = Field(
        ...,
        description="Total amount pending"
    )
    total_refunded: Decimal = Field(
        ...,
        description="Total amount refunded"
    )
    total_failed: Decimal = Field(
        ...,
        description="Total amount from failed payments"
    )
    currency: str = Field(
        ...,
        description="Currency code for all amounts"
    )
    payment_count: int = Field(
        ...,
        description="Total number of payment records"
    )

    model_config = ConfigDict(from_attributes=True)
