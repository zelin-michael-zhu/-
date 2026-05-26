"""agent orchestrator and portal action gate

Revision ID: 0003_agent_portal_actions
Revises: 0002_documents_recommendations
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import mysql

revision = "0003_agent_portal_actions"
down_revision = "0002_documents_recommendations"
branch_labels = None
depends_on = None


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    return table in inspect(bind).get_table_names()


def _drop_if_exists(table: str) -> None:
    if _has_table(table):
        op.drop_table(table)


def upgrade() -> None:
    if not _has_table("application_plans"):
        op.create_table(
            "application_plans",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("applicant_id", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default="draft"),
            sa.Column("selected_program_ids_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("generated_recommendations_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("global_missing_documents_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("next_actions_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["applicant_id"], ["applicants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_application_plans_applicant_id", "application_plans", ["applicant_id"])
        op.create_index("ix_application_plans_status", "application_plans", ["status"])

    if not _has_table("agent_tasks"):
        op.create_table(
            "agent_tasks",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("application_plan_id", sa.Integer(), nullable=True),
            sa.Column("applicant_id", sa.Integer(), nullable=False),
            sa.Column("program_id", sa.Integer(), nullable=True),
            sa.Column("task_type", sa.String(length=80), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default="pending"),
            sa.Column("risk_level", sa.String(length=40), nullable=True),
            sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("blocked", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("input_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("result_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("logs_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["application_plan_id"], ["application_plans.id"]),
            sa.ForeignKeyConstraint(["applicant_id"], ["applicants.id"]),
            sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_agent_tasks_application_plan_id", "agent_tasks", ["application_plan_id"])
        op.create_index("ix_agent_tasks_applicant_id", "agent_tasks", ["applicant_id"])
        op.create_index("ix_agent_tasks_program_id", "agent_tasks", ["program_id"])
        op.create_index("ix_agent_tasks_task_type", "agent_tasks", ["task_type"])
        op.create_index("ix_agent_tasks_status", "agent_tasks", ["status"])
        op.create_index("ix_agent_tasks_risk_level", "agent_tasks", ["risk_level"])

    if not _has_table("audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("applicant_id", sa.Integer(), nullable=True),
            sa.Column("application_plan_id", sa.Integer(), nullable=True),
            sa.Column("agent_task_id", sa.Integer(), nullable=True),
            sa.Column("actor", sa.String(length=40), nullable=False, server_default="system"),
            sa.Column("action", sa.String(length=160), nullable=False),
            sa.Column("risk_level", sa.String(length=40), nullable=True),
            sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("approved_by_user", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("blocked", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("metadata_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["applicant_id"], ["applicants.id"]),
            sa.ForeignKeyConstraint(["application_plan_id"], ["application_plans.id"]),
            sa.ForeignKeyConstraint(["agent_task_id"], ["agent_tasks.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_audit_logs_applicant_id", "audit_logs", ["applicant_id"])
        op.create_index("ix_audit_logs_application_plan_id", "audit_logs", ["application_plan_id"])
        op.create_index("ix_audit_logs_agent_task_id", "audit_logs", ["agent_task_id"])
        op.create_index("ix_audit_logs_actor", "audit_logs", ["actor"])
        op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
        op.create_index("ix_audit_logs_risk_level", "audit_logs", ["risk_level"])

    if not _has_table("portal_sessions"):
        op.create_table(
            "portal_sessions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("applicant_id", sa.Integer(), nullable=False),
            sa.Column("program_id", sa.Integer(), nullable=True),
            sa.Column("executor_type", sa.String(length=40), nullable=False, server_default="mock"),
            sa.Column("portal_url", sa.String(length=900), nullable=True),
            sa.Column("status", sa.String(length=60), nullable=False, server_default="not_started"),
            sa.Column("last_page_url", sa.String(length=900), nullable=True),
            sa.Column("last_snapshot_text", mysql.LONGTEXT(), nullable=True),
            sa.Column("last_screenshot_path", sa.String(length=700), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["applicant_id"], ["applicants.id"]),
            sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_portal_sessions_applicant_id", "portal_sessions", ["applicant_id"])
        op.create_index("ix_portal_sessions_program_id", "portal_sessions", ["program_id"])
        op.create_index("ix_portal_sessions_executor_type", "portal_sessions", ["executor_type"])
        op.create_index("ix_portal_sessions_status", "portal_sessions", ["status"])

    if not _has_table("email_tracking_rules"):
        op.create_table(
            "email_tracking_rules",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("applicant_id", sa.Integer(), nullable=False),
            sa.Column("program_id", sa.Integer(), nullable=True),
            sa.Column("sender_pattern", sa.String(length=255), nullable=True),
            sa.Column("subject_keywords_json", mysql.LONGTEXT(), nullable=True),
            sa.Column("status", sa.String(length=40), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["applicant_id"], ["applicants.id"]),
            sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_email_tracking_rules_applicant_id", "email_tracking_rules", ["applicant_id"])
        op.create_index("ix_email_tracking_rules_program_id", "email_tracking_rules", ["program_id"])
        op.create_index("ix_email_tracking_rules_status", "email_tracking_rules", ["status"])

    if not _has_table("pending_actions"):
        op.create_table(
            "pending_actions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("applicant_id", sa.Integer(), nullable=False),
            sa.Column("program_id", sa.Integer(), nullable=True),
            sa.Column("portal_session_id", sa.Integer(), nullable=True),
            sa.Column("agent_task_id", sa.Integer(), nullable=True),
            sa.Column("action_type", sa.String(length=80), nullable=False),
            sa.Column("target_label", sa.String(length=255), nullable=True),
            sa.Column("target_selector", sa.String(length=500), nullable=True),
            sa.Column("proposed_value", sa.Text(), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("risk_level", sa.String(length=40), nullable=False, server_default="low"),
            sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("blocked", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default="pending"),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["applicant_id"], ["applicants.id"]),
            sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
            sa.ForeignKeyConstraint(["portal_session_id"], ["portal_sessions.id"]),
            sa.ForeignKeyConstraint(["agent_task_id"], ["agent_tasks.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_pending_actions_applicant_id", "pending_actions", ["applicant_id"])
        op.create_index("ix_pending_actions_program_id", "pending_actions", ["program_id"])
        op.create_index("ix_pending_actions_portal_session_id", "pending_actions", ["portal_session_id"])
        op.create_index("ix_pending_actions_agent_task_id", "pending_actions", ["agent_task_id"])
        op.create_index("ix_pending_actions_action_type", "pending_actions", ["action_type"])
        op.create_index("ix_pending_actions_risk_level", "pending_actions", ["risk_level"])
        op.create_index("ix_pending_actions_blocked", "pending_actions", ["blocked"])
        op.create_index("ix_pending_actions_status", "pending_actions", ["status"])


def downgrade() -> None:
    _drop_if_exists("pending_actions")
    _drop_if_exists("email_tracking_rules")
    _drop_if_exists("portal_sessions")
    _drop_if_exists("audit_logs")
    _drop_if_exists("agent_tasks")
    _drop_if_exists("application_plans")
