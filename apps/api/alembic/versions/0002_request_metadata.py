# -*- coding: utf-8 -*-
"""Add request metadata columns to usage_records.

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-25
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("usage_records", sa.Column("request_id", sa.String(32), nullable=True))
    op.add_column("usage_records", sa.Column("domain", sa.String(256), nullable=True))
    op.add_column("usage_records", sa.Column("validation_valid", sa.Boolean, nullable=True))
    op.add_column("usage_records", sa.Column("model", sa.String(64), nullable=True))
    op.add_column("usage_records", sa.Column("fetch_strategy", sa.String(32), nullable=True))
    op.add_column(
        "usage_records",
        sa.Column("cache_hit", sa.Boolean, nullable=False, server_default="false"),
    )
    op.add_column(
        "usage_records",
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_index("ix_usage_request_id", "usage_records", ["request_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_usage_request_id", table_name="usage_records")
    op.drop_column("usage_records", "metadata")
    op.drop_column("usage_records", "cache_hit")
    op.drop_column("usage_records", "fetch_strategy")
    op.drop_column("usage_records", "model")
    op.drop_column("usage_records", "validation_valid")
    op.drop_column("usage_records", "domain")
    op.drop_column("usage_records", "request_id")
