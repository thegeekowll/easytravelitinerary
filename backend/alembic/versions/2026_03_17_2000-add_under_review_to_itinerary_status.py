"""add under_review to itinerary status enum

Revision ID: add_under_review_status
Revises: 2026_03_17_1000
Create Date: 2026-03-17 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_under_review_status'
down_revision = '2026_03_17_1000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add UNDER_REVIEW value to the existing PostgreSQL enum
    op.execute("ALTER TYPE itinerary_status_enum ADD VALUE IF NOT EXISTS 'UNDER_REVIEW'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values without recreating the type.
    # To downgrade, you would need to manually remove the enum value.
    pass
