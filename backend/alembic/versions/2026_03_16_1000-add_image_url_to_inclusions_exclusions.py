"""Add image_url to inclusions and exclusions tables

Revision ID: a1b2c3d4e5f6
Revises: f963fdf0c88e
Create Date: 2026-03-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f963fdf0c88e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use raw SQL with IF NOT EXISTS to be safe in all environments
    op.execute("ALTER TABLE inclusions ADD COLUMN IF NOT EXISTS image_url TEXT")
    op.execute("ALTER TABLE exclusions ADD COLUMN IF NOT EXISTS image_url TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE exclusions DROP COLUMN IF EXISTS image_url")
    op.execute("ALTER TABLE inclusions DROP COLUMN IF EXISTS image_url")
