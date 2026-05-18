# -*- coding: utf-8 -*-
"""Initial schema: accounts, oauth_accounts, api_keys, usage_records, webhook_endpoints

Revision ID: 0001
Revises:
Create Date: 2026-05-18
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("tier", sa.String(32), nullable=False, server_default="free"),
        sa.Column("stripe_customer_id", sa.String(64), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(64), nullable=True),
        sa.Column("stripe_billing_anchor", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_reported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_accounts_email", "accounts", ["email"], unique=True)

    op.create_table(
        "oauth_accounts",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("account_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("provider_account_id", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_oauth_provider_account", "oauth_accounts", ["provider", "provider_account_id"], unique=True)

    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("account_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("label", sa.String(64), nullable=False, server_default="default"),
        sa.Column("key_hash", sa.String(128), nullable=False),
        sa.Column("key_prefix", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_api_keys_prefix", "api_keys", ["key_prefix"])

    op.create_table(
        "usage_records",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("account_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("api_key_id", sa.String(16), sa.ForeignKey("api_keys.id"), nullable=True),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("layer", sa.Integer, nullable=False),
        sa.Column("success", sa.Boolean, nullable=False),
        sa.Column("credits_used", sa.Integer, nullable=False, server_default="1"),
        sa.Column("response_time_ms", sa.Integer, nullable=True),
        sa.Column("error_code", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_usage_account_created", "usage_records", ["account_id", "created_at"])
    op.create_index("ix_usage_key_created", "usage_records", ["api_key_id", "created_at"])

    op.create_table(
        "webhook_endpoints",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("account_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("secret", sa.String(64), nullable=False),
        sa.Column("events", sa.String(256), nullable=False, server_default="*"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("webhook_endpoints")
    op.drop_index("ix_usage_key_created", "usage_records")
    op.drop_index("ix_usage_account_created", "usage_records")
    op.drop_table("usage_records")
    op.drop_index("ix_api_keys_prefix", "api_keys")
    op.drop_table("api_keys")
    op.drop_index("ix_oauth_provider_account", "oauth_accounts")
    op.drop_table("oauth_accounts")
    op.drop_index("ix_accounts_email", "accounts")
    op.drop_table("accounts")
