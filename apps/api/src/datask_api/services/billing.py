# -*- coding: utf-8 -*-
"""
Stripe billing service.
Checkout session creation, webhook handling, usage summary.
"""
import calendar
from datetime import UTC, datetime
from typing import Any

import stripe
import structlog
from datask_core.config import get_settings
from datask_api.db.repositories import accounts as accounts_repo
from datask_api.db.repositories import usage as usage_repo
from datask_api.db.session import get_session_factory

logger = structlog.get_logger()


def _init_stripe() -> None:
    settings = get_settings()
    stripe.api_key = settings.stripe_secret_key


async def create_checkout_session(account_id: str) -> str:
    """
    Tạo Stripe Checkout session cho PAYG tier upgrade.
    Returns session URL để redirect user.
    """
    _init_stripe()
    settings = get_settings()

    factory = get_session_factory()
    async with factory() as session:
        account = await accounts_repo.get_by_id(session, account_id)
        email = account.email if account else None

    checkout_params: dict[str, Any] = {
        "mode": "subscription",
        "payment_method_types": ["card"],
        "line_items": [{"price": settings.stripe_price_payg_id, "quantity": 1}],
        "client_reference_id": account_id,
        "success_url": f"{settings.base_url}/dashboard?upgrade=success",
        "cancel_url": f"{settings.base_url}/pricing",
        "metadata": {"account_id": account_id},
    }
    if email:
        checkout_params["customer_email"] = email

    checkout_session = stripe.checkout.Session.create(**checkout_params)
    return checkout_session.url or ""


async def handle_stripe_webhook(payload: bytes, sig_header: str) -> None:
    """
    Verify và process Stripe webhook events.
    """
    _init_stripe()
    settings = get_settings()

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except (stripe.SignatureVerificationError, ValueError) as e:
        raise ValueError(f"Invalid webhook signature: {e}") from e

    event_type: str = event["type"]
    logger.info("stripe_webhook", event_type=event_type)

    factory = get_session_factory()

    if event_type == "checkout.session.completed":
        session_data = event["data"]["object"]
        account_id = session_data.get("metadata", {}).get("account_id")
        customer_id = session_data.get("customer")
        subscription_id = session_data.get("subscription")

        if account_id:
            async with factory() as session:
                await accounts_repo.update_tier(
                    session,
                    account_id=account_id,
                    tier="payg",
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    stripe_billing_anchor=datetime.now(UTC),
                )
                await session.commit()
            logger.info("account_upgraded", account_id=account_id, tier="payg")

    elif event_type == "customer.subscription.deleted":
        customer_id = event["data"]["object"]["customer"]
        from sqlalchemy import select as sql_select
        from datask_api.models.db import Account

        async with factory() as session:
            result = await session.execute(
                sql_select(Account).where(Account.stripe_customer_id == customer_id)
            )
            account = result.scalar_one_or_none()
            if account:
                await accounts_repo.update_tier(session, account.id, tier="free")
                await session.commit()
                logger.info("account_downgraded", account_id=account.id)

    elif event_type == "invoice.payment_succeeded":
        logger.info("invoice_paid", customer=event["data"]["object"].get("customer"))


def _next_billing_date(anchor_day: int, from_now: datetime) -> datetime:
    """
    Tính ngày billing tiếp theo dựa trên anchor_day.
    Nếu anchor_day đã qua trong tháng này → tháng sau.
    Nếu anchor_day chưa tới → tháng này.
    """
    year, month, day = from_now.year, from_now.month, from_now.day

    if day >= anchor_day:
        # Anchor already passed this month — next billing is next month
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1

    last_day_of_month = calendar.monthrange(year, month)[1]
    billing_day = min(anchor_day, last_day_of_month)
    return from_now.replace(year=year, month=month, day=billing_day, hour=0, minute=0, second=0, microsecond=0)


async def get_usage_summary(account_id: str) -> dict[str, Any]:
    """Lấy usage summary thật từ DB."""
    factory = get_session_factory()
    async with factory() as session:
        account = await accounts_repo.get_by_id(session, account_id)
        if not account:
            return {
                "current_month_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "credits_used": 0,
                "quota_remaining": 500,
                "tier": "free",
                "billing_period_end": None,
            }

        summary = await usage_repo.get_summary(session, account_id)
        settings = get_settings()

        quota_remaining = None
        if account.tier == "free":
            quota_remaining = max(
                0,
                settings.free_tier_monthly_quota - summary["successful_requests"],
            )

        billing_period_end = None
        if account.stripe_billing_anchor:
            next_date = _next_billing_date(
                anchor_day=account.stripe_billing_anchor.day,
                from_now=datetime.now(UTC),
            )
            billing_period_end = next_date.isoformat()

        return {
            **summary,
            "quota_remaining": quota_remaining,
            "tier": account.tier,
            "billing_period_end": billing_period_end,
        }
