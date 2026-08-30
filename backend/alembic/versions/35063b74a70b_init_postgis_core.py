"""init_postgis_core

Revision ID: 35063b74a70b
Revises: 
Create Date: 2026-08-28 16:55:35
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '35063b74a70b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
        op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.create_table(
        "system_configurations",
        sa.Column("key", sa.Text, primary_key=True),
        sa.Column("value", sa.JSON, nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("updated_by", sa.Text, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("actor_id", sa.Text, nullable=True),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("entity", sa.Text, nullable=False),
        sa.Column("entity_id", sa.Text, nullable=True),
        sa.Column("before", sa.JSON, nullable=True),
        sa.Column("after", sa.JSON, nullable=True),
        sa.Column("request_id", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("aggregate", sa.Text, nullable=False),
        sa.Column("aggregate_id", sa.Text, nullable=False),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default="PENDING"),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_outbox_events_status", "outbox_events", ["status"])

def downgrade() -> None:
    op.drop_index("ix_outbox_events_status", table_name="outbox_events")
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_table("outbox_events")
    op.drop_table("audit_logs")
    op.drop_table("system_configurations")
    op.execute("DROP EXTENSION IF EXISTS postgis")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
