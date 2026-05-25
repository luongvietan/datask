# -*- coding: utf-8 -*-
"""Unit tests cho budget alerts — mock email + Redis dedup."""
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from datask_api.db.repositories import accounts as accounts_repo
from datask_api.db.repositories import usage as usage_repo


# ---------------------------------------------------------------------------
# Helpers — mock Redis as a simple in-memory dict
# ---------------------------------------------------------------------------


class FakeRedis:
    """Minimal async Redis mock for budget alert tests."""

    def __init__(self):
        self._store: dict[str, str] = {}
        self._ttls: dict[str, int] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = value
        self._ttls[key] = ttl

    async def exists(self, key: str) -> int:
        return 1 if key in self._store else 0

    async def ping(self) -> bool:
        return True

    async def incrby(self, key: str, amount: int) -> int:
        val = int(self._store.get(key, "0"))
        val += amount
        self._store[key] = str(val)
        return val

    async def expire(self, key: str, ttl: int) -> None:
        self._ttls[key] = ttl

    def pipeline(self):
        return FakeRedisPipeline(self)


class FakeRedisPipeline:
    def __init__(self, redis: FakeRedis):
        self._redis = redis
        self._ops: list = []

    def incrby(self, key: str, amount: int):
        self._ops.append(("incrby", key, amount))
        return self

    def expire(self, key: str, ttl: int):
        self._ops.append(("expire", key, ttl))
        return self

    async def execute(self):
        results = []
        for op in self._ops:
            if op[0] == "incrby":
                results.append(await self._redis.incrby(op[1], op[2]))
            elif op[0] == "expire":
                await self._redis.expire(op[1], op[2])
                results.append(True)
        return results


# ---------------------------------------------------------------------------
# Tests: get_budget_usage() returns alert_level
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_budget_usage_returns_alert_level_none(db_session: AsyncSession) -> None:
    """Under threshold → alert_level = 'none'."""
    from datask_api.services.budget import get_budget_usage

    account = await accounts_repo.create(db_session, email="alert-none@example.com")
    await accounts_repo.update_budget(
        db_session, account_id=account.id, monthly_credit_budget=100, budget_alert_threshold=80,
    )
    await usage_repo.insert_record(
        db_session, account_id=account.id, api_key_id=None, url="https://x.com",
        layer=2, success=True, credits_used=50,
    )
    await db_session.commit()

    fake_redis = FakeRedis()
    fake_redis._store[f"budget:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"] = "50"

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory:
        mock_factory.return_value = _make_context_manager(db_session)
        result = await get_budget_usage(account.id)

    assert result["alert_level"] == "none"
    assert result["used"] == 50


@pytest.mark.asyncio
async def test_get_budget_usage_returns_alert_level_warning(db_session: AsyncSession) -> None:
    """At 80% threshold → alert_level = 'warning'."""
    from datask_api.services.budget import get_budget_usage

    account = await accounts_repo.create(db_session, email="alert-warn@example.com")
    await accounts_repo.update_budget(
        db_session, account_id=account.id, monthly_credit_budget=100, budget_alert_threshold=80,
    )
    await usage_repo.insert_record(
        db_session, account_id=account.id, api_key_id=None, url="https://x.com",
        layer=2, success=True, credits_used=80,
    )
    await db_session.commit()

    fake_redis = FakeRedis()
    fake_redis._store[f"budget:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"] = "80"

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory:
        mock_factory.return_value = _make_context_manager(db_session)
        result = await get_budget_usage(account.id)

    assert result["alert_level"] == "warning"


@pytest.mark.asyncio
async def test_get_budget_usage_returns_alert_level_exceeded(db_session: AsyncSession) -> None:
    """At 100% → alert_level = 'exceeded'."""
    from datask_api.services.budget import get_budget_usage

    account = await accounts_repo.create(db_session, email="alert-exceed@example.com")
    await accounts_repo.update_budget(
        db_session, account_id=account.id, monthly_credit_budget=100, budget_alert_threshold=80,
    )
    await usage_repo.insert_record(
        db_session, account_id=account.id, api_key_id=None, url="https://x.com",
        layer=2, success=True, credits_used=100,
    )
    await db_session.commit()

    fake_redis = FakeRedis()
    fake_redis._store[f"budget:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"] = "100"

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory:
        mock_factory.return_value = _make_context_manager(db_session)
        result = await get_budget_usage(account.id)

    assert result["alert_level"] == "exceeded"


@pytest.mark.asyncio
async def test_get_budget_usage_no_budget_no_alert(db_session: AsyncSession) -> None:
    """No budget set (NULL) → no alert_level in result."""
    from datask_api.services.budget import get_budget_usage

    account = await accounts_repo.create(db_session, email="no-budget@example.com")
    await db_session.commit()

    with patch("datask_api.services.budget.get_session_factory") as mock_factory:
        mock_factory.return_value = _make_context_manager(db_session)
        result = await get_budget_usage(account.id)

    assert result["budget"] is None


@pytest.mark.asyncio
async def test_get_budget_usage_custom_threshold(db_session: AsyncSession) -> None:
    """Custom threshold 90% → warning at 90, not 80."""
    from datask_api.services.budget import get_budget_usage

    account = await accounts_repo.create(db_session, email="custom-thresh@example.com")
    await accounts_repo.update_budget(
        db_session, account_id=account.id, monthly_credit_budget=100, budget_alert_threshold=90,
    )
    await db_session.commit()

    fake_redis = FakeRedis()
    fake_redis._store[f"budget:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"] = "85"

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory:
        mock_factory.return_value = _make_context_manager(db_session)
        result = await get_budget_usage(account.id)

    assert result["alert_level"] == "none"

    fake_redis._store[f"budget:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"] = "91"

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory:
        mock_factory.return_value = _make_context_manager(db_session)
        result = await get_budget_usage(account.id)

    assert result["alert_level"] == "warning"


# ---------------------------------------------------------------------------
# Tests: check_budget_alerts() — email + dedup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_budget_alerts_sends_warning(db_session: AsyncSession) -> None:
    """check_budget_alerts sends email and sets dedup key at warning threshold."""
    from datask_api.services.budget import check_budget_alerts

    account = await accounts_repo.create(db_session, email="warn-send@example.com")
    account.tier = "payg"
    await accounts_repo.update_budget(
        db_session, account_id=account.id, monthly_credit_budget=100, budget_alert_threshold=80,
    )
    await db_session.commit()

    fake_redis = FakeRedis()
    fake_redis._store[f"budget:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"] = "85"

    mock_email = AsyncMock()

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory, \
         patch("datask_api.services.email.send_budget_alert", mock_email):
        mock_factory.return_value = _make_context_manager(db_session)
        level = await check_budget_alerts(account.id)

    assert level == "warning"
    mock_email.assert_awaited_once()
    call_kwargs = mock_email.call_args.kwargs
    assert call_kwargs["pct"] == 85

    month_key = f"budget:alert:warning:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"
    assert month_key in fake_redis._store


@pytest.mark.asyncio
async def test_check_budget_alerts_sends_exceeded(db_session: AsyncSession) -> None:
    """check_budget_alerts sends email at 100%."""
    from datask_api.services.budget import check_budget_alerts

    account = await accounts_repo.create(db_session, email="exceed-send@example.com")
    account.tier = "payg"
    await accounts_repo.update_budget(
        db_session, account_id=account.id, monthly_credit_budget=100, budget_alert_threshold=80,
    )
    await db_session.commit()

    fake_redis = FakeRedis()
    fake_redis._store[f"budget:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"] = "100"

    mock_email = AsyncMock()

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory, \
         patch("datask_api.services.email.send_budget_alert", mock_email):
        mock_factory.return_value = _make_context_manager(db_session)
        level = await check_budget_alerts(account.id)

    assert level == "exceeded"
    mock_email.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_budget_alerts_dedup_no_duplicate(db_session: AsyncSession) -> None:
    """Second call does NOT send email again — dedup key prevents spam."""
    from datask_api.services.budget import check_budget_alerts

    account = await accounts_repo.create(db_session, email="dedup@example.com")
    account.tier = "payg"
    await accounts_repo.update_budget(
        db_session, account_id=account.id, monthly_credit_budget=100, budget_alert_threshold=80,
    )
    await db_session.commit()

    fake_redis = FakeRedis()
    fake_redis._store[f"budget:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"] = "85"

    month_key = f"budget:alert:warning:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"

    mock_email = AsyncMock()

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory, \
         patch("datask_api.services.email.send_budget_alert", mock_email):
        mock_factory.return_value = _make_context_manager(db_session)

        level1 = await check_budget_alerts(account.id)
        assert level1 == "warning"
        assert mock_email.await_count == 1

        level2 = await check_budget_alerts(account.id)
        assert level2 == "warning"
        assert mock_email.await_count == 1, "Email should NOT be sent again (dedup)"


@pytest.mark.asyncio
async def test_check_budget_alerts_no_budget_no_alert(db_session: AsyncSession) -> None:
    """Account with NULL budget → no alert sent."""
    from datask_api.services.budget import check_budget_alerts

    account = await accounts_repo.create(db_session, email="no-budget@example.com")
    account.tier = "payg"
    await db_session.commit()

    fake_redis = FakeRedis()
    mock_email = AsyncMock()

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory, \
         patch("datask_api.services.email.send_budget_alert", mock_email):
        mock_factory.return_value = _make_context_manager(db_session)
        level = await check_budget_alerts(account.id)

    assert level == "none"
    mock_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_check_budget_alerts_free_tier_skipped(db_session: AsyncSession) -> None:
    """Free tier accounts skip budget alert check entirely."""
    from datask_api.services.budget import check_budget_alerts

    account = await accounts_repo.create(db_session, email="free@example.com")
    assert account.tier == "free"
    await db_session.commit()

    fake_redis = FakeRedis()
    mock_email = AsyncMock()

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory, \
         patch("datask_api.services.email.send_budget_alert", mock_email):
        mock_factory.return_value = _make_context_manager(db_session)
        level = await check_budget_alerts(account.id)

    assert level == "none"
    mock_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_check_budget_alerts_under_threshold_no_alert(db_session: AsyncSession) -> None:
    """Usage under threshold → no email sent."""
    from datask_api.services.budget import check_budget_alerts

    account = await accounts_repo.create(db_session, email="under@example.com")
    account.tier = "payg"
    await accounts_repo.update_budget(
        db_session, account_id=account.id, monthly_credit_budget=100, budget_alert_threshold=80,
    )
    await db_session.commit()

    fake_redis = FakeRedis()
    fake_redis._store[f"budget:{account.id}:{datetime.now(UTC).strftime('%Y-%m')}"] = "50"

    mock_email = AsyncMock()

    with patch("datask_api.services.budget._get_redis", return_value=fake_redis), \
         patch("datask_api.services.budget.get_session_factory") as mock_factory, \
         patch("datask_api.services.email.send_budget_alert", mock_email):
        mock_factory.return_value = _make_context_manager(db_session)
        level = await check_budget_alerts(account.id)

    assert level == "none"
    mock_email.assert_not_awaited()


# ---------------------------------------------------------------------------
# Tests: send_budget_alert() — email service
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_budget_alert_console_log() -> None:
    """Without RESEND_API_KEY, alert logs to console instead of sending."""
    from datask_api.services.email import send_budget_alert

    with patch.dict("os.environ", {"RESEND_API_KEY": ""}, clear=False):
        await send_budget_alert(
            account_id="test-123",
            email="user@example.com",
            pct=85,
            budget=100,
            used=85,
        )


@pytest.mark.asyncio
async def test_send_budget_alert_exceeded_console_log() -> None:
    """Exceeded alert logs correct message."""
    from datask_api.services.email import send_budget_alert

    with patch.dict("os.environ", {"RESEND_API_KEY": ""}, clear=False):
        await send_budget_alert(
            account_id="test-456",
            email="user@example.com",
            pct=100,
            budget=100,
            used=100,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_context_manager(session):
    """Wrap a session in an async context manager for get_session_factory mock."""
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _ctx():
        yield session

    return _ctx
