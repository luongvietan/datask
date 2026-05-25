# -*- coding: utf-8 -*-
"""
Billing routes — Stripe checkout + usage summary.
"""
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from datask_api.middleware.auth import get_current_key
from datask_api.services.billing import (
    create_checkout_session,
    get_usage_summary,
    handle_stripe_webhook,
)

router = APIRouter()


@router.get(
    "/billing/usage",
    summary="Get current billing period usage summary",
)
async def usage_summary(
    current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    summary = await get_usage_summary(current_key["account_id"])
    return JSONResponse(content=summary)


@router.post(
    "/billing/checkout",
    summary="Create a Stripe Checkout session for plan upgrade",
)
async def create_checkout(
    current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    url = await create_checkout_session(current_key["account_id"])
    return JSONResponse(content={"checkout_url": url})


@router.get(
    "/billing/domains",
    summary="Top domains by request count this month",
)
async def top_domains_endpoint(
    current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    from datask_api.db.repositories import usage as usage_repo
    from datask_api.db.session import get_session_factory
    factory = get_session_factory()
    async with factory() as session:
        domains = await usage_repo.top_domains(session, current_key["account_id"])
    return JSONResponse(content={"domains": domains})


@router.get(
    "/billing/history",
    summary="Daily request counts for the last 30 days",
)
async def usage_history(
    current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    from datask_api.db.session import get_session_factory
    from datask_api.models.db import UsageRecord
    from sqlalchemy import func, select, cast, Date, Integer
    from datetime import UTC, datetime, timedelta

    factory = get_session_factory()
    account_id = current_key["account_id"]
    now = datetime.now(UTC)
    since = now - timedelta(days=30)

    async with factory() as session:
        result = await session.execute(
            select(
                cast(UsageRecord.created_at, Date).label("date"),
                func.count(UsageRecord.id).label("requests"),
                func.sum(cast(UsageRecord.success, Integer)).label("successful"),
            )
            .where(
                UsageRecord.account_id == account_id,
                UsageRecord.created_at >= since,
            )
            .group_by(cast(UsageRecord.created_at, Date))
            .order_by(cast(UsageRecord.created_at, Date))
        )
        rows = result.all()

    history = [
        {
            "date": str(row.date),
            "requests": row.requests,
            "successful": int(row.successful or 0),
        }
        for row in rows
    ]
    return JSONResponse(content={"history": history})


@router.post(
    "/billing/stripe/webhook",
    summary="Stripe webhook event handler",
    include_in_schema=False,
)
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(None, alias="Stripe-Signature"),
) -> JSONResponse:
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    payload = await request.body()

    try:
        await handle_stripe_webhook(payload, stripe_signature)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"received": True})
