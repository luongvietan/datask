# -*- coding: utf-8 -*-
"""Expand usage_records.api_key_id to support session keys.

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-26
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("usage_records_api_key_id_fkey", "usage_records", type_="foreignkey")
    op.alter_column(
        "usage_records",
        "api_key_id",
        type_=sa.String(64),
        existing_type=sa.String(16),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "usage_records",
        "api_key_id",
        type_=sa.String(16),
        existing_type=sa.String(64),
        existing_nullable=True,
    )
    op.create_foreign_key(
        "usage_records_api_key_id_fkey",
        "usage_records",
        "api_keys",
        ["api_key_id"],
        ["id"],
    )
