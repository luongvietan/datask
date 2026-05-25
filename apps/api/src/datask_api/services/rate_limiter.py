# -*- coding: utf-8 -*-
"""
Redis sliding-window rate limiter.
Returns (allowed: bool, retry_after_seconds: int).

When Redis is unavailable the limiter fails open — all requests are allowed.
This keeps the API functional during local development without Redis.
"""
import asyncio
import logging
import time

import redis.asyncio as aioredis
from datask_core.config import get_settings

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None
_redis_init_lock = asyncio.Lock()

TIER_BURST_PER_MINUTE: dict[str, int] = {
    "free": 10,
    "payg": 60,
    "commit_10k": 120,
    "commit_100k": 300,
}


def _clear_redis_client() -> None:
    """Reset the cached Redis client so the next call re-attempts the connection."""
    global _redis_client
    _redis_client = None


async def _get_redis() -> aioredis.Redis | None:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    async with _redis_init_lock:
        if _redis_client is not None:
            return _redis_client
        try:
            settings = get_settings()
            client = aioredis.from_url(settings.redis_url, decode_responses=True)
            await client.ping()
            _redis_client = client
        except Exception as exc:
            logger.warning("Redis unavailable — rate limiting disabled: %s", exc)
            return None
    return _redis_client


async def check_ip_rate_limit(
    client_ip: str,
    window_seconds: int = 60,
) -> tuple[bool, int]:
    """Layer 1 free tier: sliding window per IP. Fails open if Redis is down."""
    redis = await _get_redis()
    if redis is None:
        return True, 0

    try:
        settings = get_settings()
        limit = settings.free_tier_burst_per_minute
        key = f"ratelimit:ip:{client_ip}"
        now = time.time()
        window_start = now - window_seconds

        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window_seconds * 2)
        results = await pipe.execute()

        count: int = results[1]
        return (False, window_seconds) if count >= limit else (True, 0)
    except Exception as exc:
        logger.warning("IP rate limit check failed (fail open): %s", exc)
        _clear_redis_client()
        return True, 0


async def check_key_rate_limit(
    api_key_id: str,
    tier: str = "free",
    window_seconds: int = 60,
) -> tuple[bool, int]:
    """Layer 2/3: sliding window per API key. Fails open if Redis is down."""
    redis = await _get_redis()
    if redis is None:
        return True, 0

    try:
        limit = TIER_BURST_PER_MINUTE.get(tier, TIER_BURST_PER_MINUTE["free"])
        key = f"ratelimit:key:{api_key_id}"
        now = time.time()
        window_start = now - window_seconds

        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window_seconds * 2)
        results = await pipe.execute()

        count: int = results[1]
        return (False, window_seconds) if count >= limit else (True, 0)
    except Exception as exc:
        logger.warning("Key rate limit check failed (fail open): %s", exc)
        _clear_redis_client()
        return True, 0


async def get_remaining(api_key_id: str, tier: str = "free", window_seconds: int = 60) -> int:
    """Số request còn lại trong window. Returns full limit if Redis is down."""
    redis = await _get_redis()
    if redis is None:
        return TIER_BURST_PER_MINUTE.get(tier, TIER_BURST_PER_MINUTE["free"])

    try:
        limit = TIER_BURST_PER_MINUTE.get(tier, TIER_BURST_PER_MINUTE["free"])
        key = f"ratelimit:key:{api_key_id}"
        now = time.time()
        window_start = now - window_seconds

        await redis.zremrangebyscore(key, 0, window_start)
        count = await redis.zcard(key)
        return max(0, limit - count)
    except Exception as exc:
        logger.warning("get_remaining failed (returning full limit): %s", exc)
        _clear_redis_client()
        return TIER_BURST_PER_MINUTE.get(tier, TIER_BURST_PER_MINUTE["free"])
