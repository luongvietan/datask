# -*- coding: utf-8 -*-
"""
Budget cap service — kiểm tra và enforce monthly credit budget cho PAYG accounts.
Redis counter: budget:{account_id}:{YYYY-MM} INCR on billable request.
Falls back to Postgres nếu Redis unavailable.
"""
import asyncio
import logging
from calendar import monthrange
from datetime import UTC, datetime

import redis.asyncio as aioredis
from datask_core.config import get_settings

from datask_api.db.repositories import accounts as accounts_repo
from datask_api.db.repositories import usage as usage_repo
from datask_api.db.session import get_session_factory

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None
_redis_init_lock = asyncio.Lock()


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
            logger.warning("Redis unavailable for budget tracking: %s", exc)
            return None
    return _redis_client


def _budget_key(account_id: str) -> str:
    now = datetime.now(UTC)
    return f"budget:{account_id}:{now.strftime('%Y-%m')}"


def _resets_at() -> datetime:
    """Thời điểm reset budget: đầu tháng sau (UTC)."""
    now = datetime.now(UTC)
    if now.month == 12:
        return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)


async def get_budget_usage(account_id: str) -> dict:
    """
    Lấy thông tin budget usage cho account.
    Returns: {used, budget, remaining, resets_at, alert_threshold}
    """
    factory = get_session_factory()
    async with factory() as session:
        account = await accounts_repo.get_by_id(session, account_id)
        if not account:
            return {"used": 0, "budget": None, "remaining": None, "resets_at": None, "alert_threshold": 80}

        budget = account.monthly_credit_budget
        alert_threshold = account.budget_alert_threshold

        if budget is None:
            used = await usage_repo.sum_credits_current_month(session, account_id)
            return {
                "used": used,
                "budget": None,
                "remaining": None,
                "resets_at": _resets_at().isoformat(),
                "alert_threshold": alert_threshold,
            }

    redis = await _get_redis()
    if redis is not None:
        try:
            key = _budget_key(account_id)
            used = await redis.get(key)
            used = int(used) if used else 0
        except Exception:
            used = 0
            redis = None

    if redis is None:
        async with factory() as session:
            used = await usage_repo.sum_credits_current_month(session, account_id)

    remaining = max(0, budget - used)
    pct = int((used / budget) * 100) if budget > 0 else 0
    alert_level = "none"
    if pct >= 100:
        alert_level = "exceeded"
    elif pct >= alert_threshold:
        alert_level = "warning"

    return {
        "used": used,
        "budget": budget,
        "remaining": remaining,
        "resets_at": _resets_at().isoformat(),
        "alert_threshold": alert_threshold,
        "alert_level": alert_level,
    }


async def check_budget(account_id: str) -> tuple[bool, dict | None]:
    """
    Kiểm tra account có vượt budget không.
    Returns: (allowed, detail_if_exceeded)
    detail_if_exceeded = {remaining, budget, resets_at}
    """
    factory = get_session_factory()
    async with factory() as session:
        account = await accounts_repo.get_by_id(session, account_id)
        if not account:
            return True, None

        budget = account.monthly_credit_budget
        if budget is None:
            return True, None

        tier = account.tier
        if tier == "free":
            return True, None

    redis = await _get_redis()
    used = 0

    if redis is not None:
        try:
            key = _budget_key(account_id)
            val = await redis.get(key)
            used = int(val) if val else 0
        except Exception:
            redis = None

    if redis is None:
        async with factory() as session:
            used = await usage_repo.sum_credits_current_month(session, account_id)

    if used >= budget:
        return False, {
            "remaining": 0,
            "budget": budget,
            "resets_at": _resets_at().isoformat(),
        }

    return True, None


async def increment_budget(account_id: str, credits: int) -> None:
    """Tăng Redis budget counter sau khi billable request thành công."""
    redis = await _get_redis()
    if redis is None:
        return

    try:
        key = _budget_key(account_id)
        now = datetime.now(UTC)
        _, last_day = monthrange(now.year, now.month)
        end_of_month = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=0)
        ttl = int((end_of_month - now).total_seconds())

        pipe = redis.pipeline()
        pipe.incrby(key, credits)
        pipe.expire(key, max(ttl, 86400))
        await pipe.execute()
    except Exception as exc:
        logger.warning("Budget increment failed (non-fatal): %s", exc)


def _budget_alert_dedup_key(account_id: str, level: str) -> str:
    """Redis key để dedup budget alert: budget:alert:{level}:{account_id}:{YYYY-MM}"""
    now = datetime.now(UTC)
    return f"budget:alert:{level}:{account_id}:{now.strftime('%Y-%m')}"


async def check_budget_alerts(account_id: str) -> str:
    """
    Kiểm tra và gửi budget alert nếu đạt threshold.
    Returns: alert_level = "none" | "warning" | "exceeded"

    Flow:
    1. Lấy account info (budget, threshold, email, tier)
    2. Tính % usage hiện tại từ Redis/Postgres
    3. Nếu >= 100% → level = "exceeded"
    4. Nếu >= threshold% (default 80) → level = "warning"
    5. Check Redis dedup key để tránh spam
    6. Gửi email alert nếu chưa gửi trong tháng
    """
    from datask_api.services.email import send_budget_alert

    factory = get_session_factory()
    async with factory() as session:
        account = await accounts_repo.get_by_id(session, account_id)
        if not account:
            return "none"

        budget = account.monthly_credit_budget
        if budget is None or budget == 0:
            return "none"

        if account.tier == "free":
            return "none"

        email = account.email
        threshold = account.budget_alert_threshold

    redis = await _get_redis()
    used = 0

    if redis is not None:
        try:
            key = _budget_key(account_id)
            val = await redis.get(key)
            used = int(val) if val else 0
        except Exception:
            redis = None

    if redis is None:
        async with factory() as session:
            used = await usage_repo.sum_credits_current_month(session, account_id)

    pct = int((used / budget) * 100) if budget > 0 else 0

    if pct >= 100:
        level = "exceeded"
    elif pct >= threshold:
        level = "warning"
    else:
        return "none"

    if redis is None:
        logger.warning("budget_alert_check_no_redis", account_id=account_id, level=level)
        return level

    try:
        dedup_key = _budget_alert_dedup_key(account_id, level)
        already_sent = await redis.exists(dedup_key)

        if already_sent:
            logger.debug("budget_alert_already_sent", account_id=account_id, level=level)
            return level

        await send_budget_alert(
            account_id=account_id,
            email=email,
            pct=pct,
            budget=budget,
            used=used,
        )

        now = datetime.now(UTC)
        _, last_day = monthrange(now.year, now.month)
        end_of_month = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=0)
        ttl = int((end_of_month - now).total_seconds())

        await redis.setex(dedup_key, max(ttl, 86400), "sent")
        logger.info("budget_alert_sent", account_id=account_id, level=level, pct=pct)

    except Exception as exc:
        logger.warning("budget_alert_dedup_failed", account_id=account_id, error=str(exc))

    return level
