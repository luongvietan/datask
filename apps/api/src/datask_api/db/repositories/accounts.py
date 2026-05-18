# -*- coding: utf-8 -*-
"""Repository cho bảng accounts + oauth_accounts."""
import secrets
from datetime import UTC, datetime

from datask_api.models.db import Account, OAuthAccount
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def get_by_id(session: AsyncSession, account_id: str) -> Account | None:
    result = await session.execute(select(Account).where(Account.id == account_id))
    return result.scalar_one_or_none()


async def get_by_email(session: AsyncSession, email: str) -> Account | None:
    result = await session.execute(select(Account).where(Account.email == email))
    return result.scalar_one_or_none()


async def get_by_oauth(
    session: AsyncSession, provider: str, provider_account_id: str
) -> Account | None:
    """Tìm account qua OAuth provider account."""
    result = await session.execute(
        select(Account)
        .join(OAuthAccount, OAuthAccount.account_id == Account.id)
        .where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_account_id == provider_account_id,
        )
    )
    return result.scalar_one_or_none()


async def create(session: AsyncSession, email: str, email_verified: bool = False) -> Account:
    account = Account(
        id=secrets.token_hex(16),
        email=email,
        email_verified=email_verified,
        tier="free",
    )
    session.add(account)
    await session.flush()
    return account


async def upsert_oauth(
    session: AsyncSession,
    account_id: str,
    provider: str,
    provider_account_id: str,
) -> OAuthAccount:
    """Tạo OAuthAccount nếu chưa có."""
    result = await session.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_account_id == provider_account_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    oauth = OAuthAccount(
        id=secrets.token_hex(16),
        account_id=account_id,
        provider=provider,
        provider_account_id=provider_account_id,
    )
    session.add(oauth)
    await session.flush()
    return oauth


async def update_tier(
    session: AsyncSession,
    account_id: str,
    tier: str,
    stripe_customer_id: str | None = None,
    stripe_subscription_id: str | None = None,
    stripe_billing_anchor: datetime | None = None,
) -> None:
    values: dict = {"tier": tier, "updated_at": datetime.utcnow()}
    if stripe_customer_id is not None:
        values["stripe_customer_id"] = stripe_customer_id
    if stripe_subscription_id is not None:
        values["stripe_subscription_id"] = stripe_subscription_id
    if stripe_billing_anchor is not None:
        values["stripe_billing_anchor"] = stripe_billing_anchor

    await session.execute(update(Account).where(Account.id == account_id).values(**values))
