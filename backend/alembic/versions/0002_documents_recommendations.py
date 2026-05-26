"""documents metadata and ai recommendations

Revision ID: 0002_documents_recommendations
Revises: 0001_initial_schema
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import mysql

revision = "0002_documents_recommendations"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    return column in {item["name"] for item in inspect(bind).get_columns(table)}


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    return table in inspect(bind).get_table_names()


def upgrade() -> None:
    additions = [
        ("original_filename", sa.Column("original_filename", sa.String(length=255), nullable=True)),
        ("stored_filename", sa.Column("stored_filename", sa.String(length=255), nullable=True)),
        ("content_type", sa.Column("content_type", sa.String(length=160), nullable=True)),
        ("file_size", sa.Column("file_size", sa.Integer(), nullable=True)),
        ("file_hash", sa.Column("file_hash", sa.String(length=80), nullable=True)),
        ("version", sa.Column("version", sa.Integer(), nullable=False, server_default="1")),
        ("notes", sa.Column("notes", sa.Text(), nullable=True)),
        ("uploaded_at", sa.Column("uploaded_at", sa.DateTime(), nullable=True)),
        ("is_active", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true())),
    ]
    for name, column in additions:
        if not _has_column("documents", name):
            op.add_column("documents", column)
    if not _has_table("ai_recommendations"):
        op.create_table(
            "ai_recommendations",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("applicant_id", sa.Integer(), nullable=False),
            sa.Column("provider", sa.String(length=80), nullable=False, server_default="mock"),
            sa.Column("recommendations_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["applicant_id"], ["applicants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ai_recommendations_applicant_id", "ai_recommendations", ["applicant_id"])
    if not _has_column("documents", "file_hash"):
        op.create_index("ix_documents_file_hash", "documents", ["file_hash"])
    if not _has_column("documents", "is_active"):
        op.create_index("ix_documents_is_active", "documents", ["is_active"])


def downgrade() -> None:
    if _has_table("ai_recommendations"):
        op.drop_index("ix_ai_recommendations_applicant_id", table_name="ai_recommendations")
        op.drop_table("ai_recommendations")
    for column in ["is_active", "uploaded_at", "notes", "version", "file_hash", "file_size", "content_type", "stored_filename", "original_filename"]:
        if _has_column("documents", column):
            op.drop_column("documents", column)
