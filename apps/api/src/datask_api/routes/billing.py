# -*- coding: utf-8 -*-
"""
Billing routes — Stripe checkout + usage summary + budget management.
"""
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from datask_api.middleware.auth import get_current_key
from datask_api.services.billing import (
    create_checkout_session,
    get_usage_summary,
    handle_stripe_webhook,
)
from datask_api.services.budget import get_budget_usage

router = APIRouter()


class BudgetUpdateRequest(BaseModel):
    monthly_credit_budget: int | None = Field(
        default=None,
        description="Monthly credit budget cap. NULL = unlimited PAYG.",
        ge=0,
    )
    budget_alert_threshold: int = Field(
        default=80,
        description="Percentage threshold for budget alert (0-100).",
        ge=0,
        le=100,
    )


@router.get(
    "/billing/usage",
    summary="Get current billing period usage summary",
)
async def usage_summary(
    current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    summary = await get_usage_summary(current_key["account_id"])
    budget_info = await get_budget_usage(current_key["account_id"])
    return JSONResponse(content={**summary, **budget_info})


@router.patch(
    "/billing/budget",
    summary="Set or update monthly credit budget cap",
)
async def update_budget(
    payload: BudgetUpdateRequest,
    current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    from datask_api.db.repositories import accounts as accounts_repo
    from datask_api.db.session import get_session_factory

    account_id = current_key["account_id"]
    factory = get_session_factory()
    async with factory() as session:
        account = await accounts_repo.get_by_id(session, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        if account.tier == "free":
            return JSONResponse(
                status_code=400,
                content={
                    "error": "budget_unavailable",
                    "message": "Budget caps are only available for paid plans.",
                },
            )

        await accounts_repo.update_budget(
            session,
            account_id=account_id,
            monthly_credit_budget=payload.monthly_credit_budget,
            budget_alert_threshold=payload.budget_alert_threshold,
        )
        await session.commit()

    budget_info = await get_budget_usage(account_id)
    return JSONResponse(content={
        "monthly_credit_budget": payload.monthly_credit_budget,
        "budget_alert_threshold": payload.budget_alert_threshold,
        **budget_info,
    })


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
