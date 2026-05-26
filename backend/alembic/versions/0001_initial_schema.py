"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-25
"""
from alembic import op
from app.core.database import Base
from app.models import *  # noqa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
