# -*- coding: utf-8 -*-
"""
Webhook delivery service.
- CRUD WebhookEndpoint
- HMAC-SHA256 signature
- Redis stream delivery với retry exponential
"""
import hashlib
import hmac
import json
import secrets
import time
from datetime import UTC, datetime
from typing import Any

import httpx
import structlog
from datask_api.db.session import get_session_factory
from datask_api.models.db import WebhookEndpoint
from sqlalchemy import delete, select

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Repository helpers
# ---------------------------------------------------------------------------


async def list_webhooks(account_id: str) -> list[dict[str, Any]]:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(WebhookEndpoint)
            .where(WebhookEndpoint.account_id == account_id)
            .order_by(WebhookEndpoint.created_at.desc())
        )
        endpoints = result.scalars().all()
        return [
            {
                "id": e.id,
                "url": e.url,
                "events": e.events,
                "is_active": e.is_active,
                "created_at": e.created_at.isoformat(),
            }
            for e in endpoints
        ]


async def create_webhook(
    account_id: str, url: str, events: str = "*"
) -> dict[str, Any]:
    factory = get_session_factory()
    async with factory() as session:
        endpoint = WebhookEndpoint(
            id=secrets.token_hex(16),
            account_id=account_id,
            url=url,
            secret=secrets.token_hex(32),
            events=events,
            is_active=True,
        )
        session.add(endpoint)
        await session.commit()
        return {
            "id": endpoint.id,
            "url": endpoint.url,
            "events": endpoint.events,
            "is_active": endpoint.is_active,
            "secret": endpoint.secret,  # Chỉ trả secret 1 lần
        }


async def delete_webhook(webhook_id: str, account_id: str) -> bool:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            delete(WebhookEndpoint)
            .where(
                WebhookEndpoint.id == webhook_id,
                WebhookEndpoint.account_id == account_id,
            )
            .returning(WebhookEndpoint.id)
        )
        await session.commit()
        return result.scalar_one_or_none() is not None


# ---------------------------------------------------------------------------
# Delivery
# ---------------------------------------------------------------------------


def _sign_payload(secret: str, payload: bytes) -> str:
    """HMAC-SHA256 signature cho webhook payload."""
    sig = hmac.HMAC(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


async def deliver_webhook(
    url: str,
    secret: str,
    event_type: str,
    data: dict[str, Any],
    max_retries: int = 3,
) -> dict[str, Any]:
    """
    Gửi webhook với HMAC-SHA256 signature.
    Retry exponential (1s, 2s, 4s) nếu thất bại.
    Returns delivery result.
    """
    payload_dict = {
        "event": event_type,
        "data": data,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    payload = json.dumps(payload_dict).encode()
    signature = _sign_payload(secret, payload)

    headers = {
        "Content-Type": "application/json",
        "X-Datask-Signature": signature,
        "X-Datask-Event": event_type,
        "User-Agent": "Datask-Webhook/1.0",
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, content=payload, headers=headers)
                if resp.is_success:
                    logger.info(
                        "webhook_delivered",
                        url=url,
                        event=event_type,
                        status=resp.status_code,
                        attempt=attempt + 1,
                    )
                    return {
                        "success": True,
                        "status_code": resp.status_code,
                        "attempts": attempt + 1,
                    }
                last_error = f"HTTP {resp.status_code}"
        except Exception as e:
            last_error = str(e)

        if attempt < max_retries - 1:
            await __import__("asyncio").sleep(2 ** attempt)

    logger.warning(
        "webhook_delivery_failed",
        url=url,
        event=event_type,
        error=last_error,
        attempts=max_retries,
    )
    return {
        "success": False,
        "error": last_error,
        "attempts": max_retries,
    }


async def dispatch_event(account_id: str, event_type: str, data: dict[str, Any]) -> None:
    """Dispatch webhook event tới tất cả active endpoints của account."""
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.account_id == account_id,
                WebhookEndpoint.is_active == True,  # noqa: E712
            )
        )
        endpoints = result.scalars().all()

    for endpoint in endpoints:
        # Filter by event type
        if endpoint.events != "*" and event_type not in endpoint.events.split(","):
            continue

        # Fire-and-forget (caller can await if needed)
        import asyncio
        asyncio.create_task(
            deliver_webhook(
                url=endpoint.url,
                secret=endpoint.secret,
                event_type=event_type,
                data=data,
            )
        )
