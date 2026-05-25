# -*- coding: utf-8 -*-
"""Add monthly credit budget caps to accounts.

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-26
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "accounts",
        sa.Column("monthly_credit_budget", sa.Integer, nullable=True),
    )
    op.add_column(
        "accounts",
        sa.Column("budget_alert_threshold", sa.Integer, nullable=False, server_default="80"),
    )


def downgrade() -> None:
    op.drop_column("accounts", "budget_alert_threshold")
    op.drop_column("accounts", "monthly_credit_budget")
