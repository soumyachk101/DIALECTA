"""initial schema — mirrors Docs/BACKEND_SCHEMA.md §2

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-20 12:30:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text(), unique=True, nullable=False),
        sa.Column("display_name", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "connected_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("encrypted_token", postgresql.BYTEA(), nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "provider", name="uq_accounts_user_provider"),
        sa.CheckConstraint("provider IN ('google_calendar','gmail')", name="ck_accounts_provider"),
    )
    op.create_index("idx_connected_accounts_user", "connected_accounts", ["user_id"])

    op.create_table(
        "user_values",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "debate_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trigger_type", sa.Text(), nullable=False),
        sa.Column("decision_summary", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="in_progress"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("trigger_type IN ('checkout','voice','manual')", name="ck_sessions_trigger"),
        sa.CheckConstraint("status IN ('in_progress','completed','failed')", name="ck_sessions_status"),
    )
    op.create_index("idx_sessions_user_created", "debate_sessions", ["user_id", sa.text("created_at DESC")])

    op.create_table(
        "debate_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debate_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent", sa.Text(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("citations", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("confidence", sa.Numeric(3, 2)),
        sa.Column("no_context_found", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("turn_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("agent IN ('optimist','skeptic','analyst','ethicist','moderator')", name="ck_turns_agent"),
    )
    op.create_index("idx_debate_turns_session", "debate_turns", ["session_id", "turn_order"])

    op.create_table(
        "decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debate_sessions.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("moderator_summary", sa.Text()),
        sa.Column("user_reported_result", sa.Text()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("outcome IN ('accepted','overridden','ignored')", name="ck_decisions_outcome"),
    )


def downgrade() -> None:
    op.drop_table("decisions")
    op.drop_index("idx_debate_turns_session", table_name="debate_turns")
    op.drop_table("debate_turns")
    op.drop_index("idx_sessions_user_created", table_name="debate_sessions")
    op.drop_table("debate_sessions")
    op.drop_table("user_values")
    op.drop_index("idx_connected_accounts_user", table_name="connected_accounts")
    op.drop_table("connected_accounts")
    op.drop_table("users")
