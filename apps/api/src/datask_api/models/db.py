# -*- coding: utf-8 -*-
"""
SQLAlchemy ORM models for Postgres.
Tables: accounts, oauth_accounts, api_keys, usage_records, webhook_endpoints
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    tier: Mapped[str] = mapped_column(String(32), default="free")  # free | payg | commit_10k | commit_100k
    stripe_customer_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stripe_billing_anchor: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    monthly_credit_budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_alert_threshold: Mapped[int] = mapped_column(Integer, default=80)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    usage_records: Mapped[list["UsageRecord"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    webhook_endpoints: Mapped[list["WebhookEndpoint"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class OAuthAccount(Base):
    """OAuth provider connections for dashboard login."""

    __tablename__ = "oauth_accounts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)           # google | github
    provider_account_id: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account: Mapped["Account"] = relationship(back_populates="oauth_accounts")

    __table_args__ = (
        Index("ix_oauth_provider_account", "provider", "provider_account_id", unique=True),
    )


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(64), default="default")
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False)     # bcrypt hash
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)    # dtsk_live_XXXXXXXX for display
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    account: Mapped["Account"] = relationship(back_populates="api_keys")
    usage_records: Mapped[list["UsageRecord"]] = relationship(back_populates="api_key")

    __table_args__ = (Index("ix_api_keys_prefix", "key_prefix"),)


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    api_key_id: Mapped[str | None] = mapped_column(ForeignKey("api_keys.id"), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    layer: Mapped[int] = mapped_column(Integer, nullable=False)            # 1, 2, or 3
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    credits_used: Mapped[int] = mapped_column(Integer, default=1)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(32), nullable=True, unique=True)
    domain: Mapped[str | None] = mapped_column(String(256), nullable=True)
    validation_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fetch_strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account: Mapped["Account"] = relationship(back_populates="usage_records")
    api_key: Mapped["ApiKey | None"] = relationship(back_populates="usage_records")

    __table_args__ = (
        Index("ix_usage_account_created", "account_id", "created_at"),
        Index("ix_usage_key_created", "api_key_id", "created_at"),
        Index("ix_usage_request_id", "request_id", unique=True),
    )


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    secret: Mapped[str] = mapped_column(String(64), nullable=False)        # HMAC signing secret
    events: Mapped[str] = mapped_column(String(256), default="*")          # comma-sep or "*"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account: Mapped["Account"] = relationship(back_populates="webhook_endpoints")
