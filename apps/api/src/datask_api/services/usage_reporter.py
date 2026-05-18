# -*- coding: utf-8 -*-
"""
Stripe usage reporter — cron chạy mỗi giờ.
Gửi delta requests lên Stripe SubscriptionItem để tránh double-count.
Sử dụng APScheduler để chạy trong process API.
"""
from datetime import UTC, datetime

import stripe
import structlog
from datask_api.db.repositories import accounts as accounts_repo
from datask_api.db.repositories import usage as usage_repo
from datask_api.db.session import get_session_factory
from datask_core.config import get_settings
from sqlalchemy import select

logger = structlog.get_logger()


async def report_usage_to_stripe() -> None:
    """
    Cho mỗi PAYG account có subscription, tính delta requests kể từ last_reported_at
    và tạo usage record trên Stripe SubscriptionItem.
    """
    settings = get_settings()
    if not settings.stripe_secret_key:
        logger.warning("stripe_usage_skip", reason="STRIPE_SECRET_KEY not set")
        return

    stripe.api_key = settings.stripe_secret_key

    factory = get_session_factory()
    from datask_api.models.db import Account

    async with factory() as session:
        result = await session.execute(
            select(Account).where(
                Account.tier == "payg",
                Account.stripe_subscription_id != None,  # noqa: E711
            )
        )
        payg_accounts = result.scalars().all()

    logger.info("stripe_usage_report_start", accounts=len(payg_accounts))

    for account in payg_accounts:
        try:
            await _report_for_account(account)
        except Exception as e:
            logger.error(
                "stripe_usage_report_failed",
                account_id=account.id,
                error=str(e),
            )


async def _report_for_account(account) -> None:  # type: ignore[no-untyped-def]
    """Report usage cho một account."""
    factory = get_session_factory()
    now = datetime.now(UTC)
    since = account.last_reported_at or account.stripe_billing_anchor or now.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    async with factory() as session:
        delta = await usage_repo.count_since(session, account.id, since)

    if delta == 0:
        logger.debug("stripe_usage_no_delta", account_id=account.id)
        return

    # Lấy subscription item ID
    subscription = stripe.Subscription.retrieve(account.stripe_subscription_id)
    items = subscription.get("items", {}).get("data", [])
    if not items:
        logger.warning("stripe_no_items", account_id=account.id)
        return

    subscription_item_id = items[0]["id"]

    stripe.SubscriptionItem.create_usage_record(
        subscription_item_id,
        quantity=delta,
        timestamp=int(now.timestamp()),
        action="increment",
    )

    # Cập nhật last_reported_at
    async with factory() as session:
        await accounts_repo.update_tier(
            session, account.id, tier=account.tier
        )
        # Manual update last_reported_at
        from sqlalchemy import update as sql_update
        from datask_api.models.db import Account
        await session.execute(
            sql_update(Account)
            .where(Account.id == account.id)
            .values(last_reported_at=now)
        )
        await session.commit()

    logger.info(
        "stripe_usage_reported",
        account_id=account.id,
        delta=delta,
        subscription_item_id=subscription_item_id,
    )


def start_usage_reporter_scheduler() -> None:
    """Khởi động APScheduler để chạy usage reporter mỗi giờ."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    import asyncio

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        report_usage_to_stripe,
        "interval",
        hours=1,
        id="stripe_usage_reporter",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("usage_reporter_scheduler_started")
