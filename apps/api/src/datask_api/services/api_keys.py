# -*- coding: utf-8 -*-
"""
API key lifecycle management.
Keys: dtsk_live_<32-char hex>
Stored as bcrypt hash. Never returned in plaintext after first creation.
Redis cache: 60s TTL per key lookup.
"""
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis
import structlog
from datask_core.config import get_settings
from datask_api.db.repositories import api_keys as keys_repo
from datask_api.db.repositories import accounts as accounts_repo
from datask_api.db.repositories.api_keys import _verify_key
from datask_api.db.session import get_session_factory

logger = structlog.get_logger()

_redis_client: aioredis.Redis | None = None
CACHE_TTL = 60  # seconds
KEY_PREFIX_LENGTH = 20


async def _get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def create_account(email: str) -> dict[str, Any]:
    """Tạo account mới trong DB."""
    factory = get_session_factory()
    async with factory() as session:
        existing = await accounts_repo.get_by_email(session, email)
        if existing:
            return {
                "id": existing.id,
                "email": existing.email,
                "tier": existing.tier,
                "created_at": existing.created_at.isoformat(),
                "message": "Account already exists.",
            }

        account = await accounts_repo.create(session, email=email)
        await session.commit()
        return {
            "id": account.id,
            "email": account.email,
            "tier": account.tier,
            "created_at": account.created_at.isoformat(),
            "message": "Account created. Check your email to verify.",
        }


async def create_api_key(account_id: str, label: str) -> dict[str, Any]:
    """Tạo API key mới, lưu bcrypt hash. Trả full key chỉ 1 lần."""
    factory = get_session_factory()
    async with factory() as session:
        key_data = await keys_repo.create(session, account_id=account_id, label=label)
        await session.commit()
    return key_data


async def list_api_keys(account_id: str) -> list[dict[str, Any]]:
    factory = get_session_factory()
    async with factory() as session:
        return await keys_repo.list_by_account(session, account_id)


async def revoke_api_key(key_id: str, account_id: str) -> None:
    """Revoke key + invalidate Redis cache ngay lập tức (O(1) delete)."""
    factory = get_session_factory()
    async with factory() as session:
        key_prefix = await keys_repo.revoke(session, key_id=key_id, account_id=account_id)
        await session.commit()

    if key_prefix:
        # Cache key là f"apikey:cache:{key_prefix}" — delete trực tiếp, O(1)
        redis = await _get_redis()
        await redis.delete(f"apikey:cache:{key_prefix}")


async def validate_api_key(raw_key: str) -> dict[str, Any] | None:
    """
    Validate API key:
    1. Check Redis cache (fast path, 60s TTL).
    2. On miss: lookup by prefix in Postgres, verify bcrypt, cache result.
    Trả về key record dict hoặc None nếu invalid/revoked.
    """
    if not raw_key.startswith("dtsk_live_"):
        return None

    prefix = raw_key[:KEY_PREFIX_LENGTH]
    cache_key = f"apikey:cache:{prefix}"

    redis = await _get_redis()
    cached = await redis.get(cache_key)
    if cached:
        try:
            data = json.loads(cached)
            # Kiểm tra key có bị revoke không (revoke xóa cache ngay)
            if data.get("is_active"):
                return data
            return None
        except Exception:
            pass

    # Cache miss — lookup từ DB
    factory = get_session_factory()
    async with factory() as session:
        candidates = await keys_repo.get_active_by_prefix(session, prefix)
        for api_key in candidates:
            if _verify_key(raw_key, api_key.key_hash):
                record = {
                    "id": api_key.id,
                    "account_id": api_key.account_id,
                    "label": api_key.label,
                    "key_prefix": api_key.key_prefix,
                    "is_active": api_key.is_active,
                    "tier": api_key.account.tier if api_key.account else "free",
                    "stripe_subscription_id": (
                        api_key.account.stripe_subscription_id if api_key.account else None
                    ),
                }
                # Cache 60s
                await redis.setex(cache_key, CACHE_TTL, json.dumps(record))
                # Update last_used_at async (fire and forget)
                await keys_repo.touch_last_used(session, api_key.id)
                await session.commit()
                return record

    return None
