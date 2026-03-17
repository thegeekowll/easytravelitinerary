"""add group_type to itineraries

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE itineraries ADD COLUMN IF NOT EXISTS group_type VARCHAR(50) NULL"
    )


def downgrade():
    op.execute("ALTER TABLE itineraries DROP COLUMN IF EXISTS group_type")
