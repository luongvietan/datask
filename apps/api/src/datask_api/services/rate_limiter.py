# -*- coding: utf-8 -*-
"""
Redis sliding-window rate limiter.
Returns (allowed: bool, retry_after_seconds: int).
"""
import asyncio
import time

import redis.asyncio as aioredis
from datask_core.config import get_settings

_redis_client: aioredis.Redis | None = None
_redis_init_lock = asyncio.Lock()

TIER_BURST_PER_MINUTE: dict[str, int] = {
    "free": 10,
    "payg": 60,
    "commit_10k": 120,
    "commit_100k": 300,
}


async def _get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        async with _redis_init_lock:
            if _redis_client is None:  # double-check after acquiring lock
                settings = get_settings()
                _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def check_ip_rate_limit(
    client_ip: str,
    window_seconds: int = 60,
) -> tuple[bool, int]:
    """Layer 1 free tier: sliding window per IP."""
    settings = get_settings()
    limit = settings.free_tier_burst_per_minute

    redis = await _get_redis()
    key = f"ratelimit:ip:{client_ip}"
    now = time.time()
    window_start = now - window_seconds

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zcard(key)
    pipe.zadd(key, {str(now): now})
    pipe.expire(key, window_seconds * 2)
    results = await pipe.execute()

    # zcard result is at index 1 (before zadd, so it's the count of existing requests)
    count: int = results[1]
    if count >= limit:
        return False, window_seconds

    return True, 0


async def check_key_rate_limit(
    api_key_id: str,
    tier: str = "free",
    window_seconds: int = 60,
) -> tuple[bool, int]:
    """Layer 2/3: sliding window per API key, burst limit theo tier."""
    limit = TIER_BURST_PER_MINUTE.get(tier, TIER_BURST_PER_MINUTE["free"])

    redis = await _get_redis()
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
    if count >= limit:
        return False, window_seconds

    return True, 0


async def get_remaining(api_key_id: str, tier: str = "free", window_seconds: int = 60) -> int:
    """Số request còn lại trong window hiện tại."""
    limit = TIER_BURST_PER_MINUTE.get(tier, TIER_BURST_PER_MINUTE["free"])
    redis = await _get_redis()
    key = f"ratelimit:key:{api_key_id}"
    now = time.time()
    window_start = now - window_seconds

    await redis.zremrangebyscore(key, 0, window_start)
    count = await redis.zcard(key)
    return max(0, limit - count)
