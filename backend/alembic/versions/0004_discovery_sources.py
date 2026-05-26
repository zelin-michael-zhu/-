"""discovery sources: add region, source_name, official_domain, status to crawl_sources

Revision ID: 0004_discovery_sources
Revises: 0003_agent_orchestrator_portal_actions
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0004_discovery_sources"
down_revision = "0003_agent_portal_actions"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    return column in {item["name"] for item in inspect(bind).get_columns(table)}


def upgrade() -> None:
    additions = [
        ("region", sa.Column("region", sa.String(length=80), nullable=True)),
        ("source_name", sa.Column("source_name", sa.String(length=255), nullable=True)),
        ("official_domain", sa.Column("official_domain", sa.String(length=500), nullable=True)),
        ("status", sa.Column("status", sa.String(length=40), nullable=False, server_default="active")),
    ]
    for name, column in additions:
        if not _has_column("crawl_sources", name):
            op.add_column("crawl_sources", column)
    if not _has_column("crawl_sources", "region"):
        op.create_index("ix_crawl_sources_region", "crawl_sources", ["region"])
    if not _has_column("crawl_sources", "status"):
        op.create_index("ix_crawl_sources_status", "crawl_sources", ["status"])


def downgrade() -> None:
    for name in ["status", "official_domain", "source_name", "region"]:
        if _has_column("crawl_sources", name):
            op.drop_column("crawl_sources", name)
