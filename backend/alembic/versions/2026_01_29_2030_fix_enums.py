"""fix enums

Revision ID: 9d88fcb2f321
Revises: 6a55fcb2f210
Create Date: 2026-01-29 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9d88fcb2f321'
down_revision = '6a55fcb2f210'
branch_labels = None
depends_on = None

def upgrade():
    # Helper for Postgres Enum modification
    # Note: This must be run with autocommit block or separate transaction handling usually, 
    # but simple execute usually works in alembic for ALTER TYPE.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE asset_type_enum ADD VALUE IF NOT EXISTS 'REVIEW_IMAGE'")
        op.execute("ALTER TYPE asset_type_enum ADD VALUE IF NOT EXISTS 'DEFAULT_IMAGE'")

def downgrade():
    # Postgres doesn't support dropping enum values
    pass
