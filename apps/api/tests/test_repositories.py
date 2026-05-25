# -*- coding: utf-8 -*-
"""Unit tests cho repositories — dùng SQLite in-memory."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from datask_api.db.repositories import accounts as accounts_repo
from datask_api.db.repositories import api_keys as keys_repo
from datask_api.db.repositories import usage as usage_repo


@pytest.mark.asyncio
async def test_create_account(db_session: AsyncSession) -> None:
    account = await accounts_repo.create(db_session, email="test@example.com")
    await db_session.commit()
    assert account.id is not None
    assert account.email == "test@example.com"
    assert account.tier == "free"


@pytest.mark.asyncio
async def test_get_account_by_email(db_session: AsyncSession) -> None:
    await accounts_repo.create(db_session, email="find@example.com")
    await db_session.commit()

    found = await accounts_repo.get_by_email(db_session, "find@example.com")
    assert found is not None
    assert found.email == "find@example.com"


@pytest.mark.asyncio
async def test_upsert_oauth(db_session: AsyncSession) -> None:
    account = await accounts_repo.create(db_session, email="oauth@example.com")
    await db_session.commit()

    oauth = await accounts_repo.upsert_oauth(db_session, account.id, "google", "google-123")
    await db_session.commit()
    assert oauth.provider == "google"
    assert oauth.provider_account_id == "google-123"

    # Idempotent
    oauth2 = await accounts_repo.upsert_oauth(db_session, account.id, "google", "google-123")
    assert oauth2.id == oauth.id


@pytest.mark.asyncio
async def test_get_account_by_oauth(db_session: AsyncSession) -> None:
    account = await accounts_repo.create(db_session, email="oauth2@example.com")
    await accounts_repo.upsert_oauth(db_session, account.id, "github", "gh-456")
    await db_session.commit()

    found = await accounts_repo.get_by_oauth(db_session, "github", "gh-456")
    assert found is not None
    assert found.id == account.id


@pytest.mark.asyncio
async def test_create_and_list_api_keys(db_session: AsyncSession) -> None:
    account = await accounts_repo.create(db_session, email="keys@example.com")
    await db_session.commit()

    key_data = await keys_repo.create(db_session, account_id=account.id, label="my-key")
    await db_session.commit()

    assert key_data["key"].startswith("dtsk_live_")
    assert key_data["is_active"] is True

    keys = await keys_repo.list_by_account(db_session, account.id)
    assert len(keys) == 1
    assert keys[0]["label"] == "my-key"


@pytest.mark.asyncio
async def test_revoke_api_key(db_session: AsyncSession) -> None:
    account = await accounts_repo.create(db_session, email="revoke@example.com")
    await db_session.commit()

    key_data = await keys_repo.create(db_session, account_id=account.id)
    await db_session.commit()

    revoked = await keys_repo.revoke(db_session, key_data["id"], account.id)
    await db_session.commit()
    assert revoked is True

    keys = await keys_repo.list_by_account(db_session, account.id)
    assert keys[0]["is_active"] is False


@pytest.mark.asyncio
async def test_usage_insert_and_count(db_session: AsyncSession) -> None:
    account = await accounts_repo.create(db_session, email="usage@example.com")
    await db_session.commit()

    for _ in range(3):
        await usage_repo.insert_record(
            db_session,
            account_id=account.id,
            api_key_id=None,
            url="https://example.com",
            layer=1,
            success=True,
        )
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://fail.com",
        layer=1,
        success=False,
    )
    await db_session.commit()

    count = await usage_repo.count_current_month(db_session, account.id)
    assert count == 3  # only successful

    summary = await usage_repo.get_summary(db_session, account.id)
    assert summary["current_month_requests"] == 4
    assert summary["successful_requests"] == 3
    assert summary["failed_requests"] == 1


@pytest.mark.asyncio
async def test_usage_insert_with_request_id(db_session: AsyncSession) -> None:
    account = await accounts_repo.create(db_session, email="reqid@example.com")
    await db_session.commit()

    record = await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://shop.example.com/product/1",
        layer=2,
        success=True,
        request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
        domain="shop.example.com",
        fetch_strategy="async",
        cache_hit=False,
        response_time_ms=1200,
    )
    await db_session.commit()

    assert record.request_id == "req_01JABCDEFGHJKMNPQRSTVWXYZ0"
    assert record.domain == "shop.example.com"
    assert record.fetch_strategy == "async"
    assert record.response_time_ms == 1200


@pytest.mark.asyncio
async def test_sum_credits_current_month_billable_only(db_session: AsyncSession) -> None:
    """sum_credits_current_month() chỉ tính rows có credits_used > 0 (billable)."""
    account = await accounts_repo.create(db_session, email="billing@example.com")
    await db_session.commit()

    # Successful L2 → credits=1 (billable)
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://ok.com/1",
        layer=2,
        success=True,
        credits_used=1,
    )
    # Successful L3 → credits=2 (billable)
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://ok.com/2",
        layer=3,
        success=True,
        credits_used=2,
    )
    # Failed job → credits=0 (NOT billable)
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://fail.com",
        layer=2,
        success=False,
        credits_used=0,
    )
    # Validation fail → credits=0 (NOT billable)
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://invalid.com",
        layer=2,
        success=True,
        credits_used=0,
        validation_valid=False,
    )
    await db_session.commit()

    total_credits = await usage_repo.sum_credits_current_month(db_session, account.id)
    assert total_credits == 3  # 1 + 2, ignoring the 0-credit rows


@pytest.mark.asyncio
async def test_get_summary_credits_billable_only(db_session: AsyncSession) -> None:
    """get_summary() credits field chỉ tính billable credits."""
    account = await accounts_repo.create(db_session, email="summary-billing@example.com")
    await db_session.commit()

    # 2 billable requests (credits=1 each)
    for _ in range(2):
        await usage_repo.insert_record(
            db_session,
            account_id=account.id,
            api_key_id=None,
            url="https://ok.com",
            layer=2,
            success=True,
            credits_used=1,
        )
    # 1 failed request (credits=0)
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://fail.com",
        layer=2,
        success=False,
        credits_used=0,
    )
    await db_session.commit()

    summary = await usage_repo.get_summary(db_session, account.id)
    assert summary["current_month_requests"] == 3
    assert summary["successful_requests"] == 2
    assert summary["failed_requests"] == 1
    assert summary["credits_used"] == 2  # chỉ billable


@pytest.mark.asyncio
async def test_sum_credits_since_billable_only(db_session: AsyncSession) -> None:
    """sum_credits_since() chỉ tính billable credits (credits_used > 0) từ thời điểm since."""
    from datetime import UTC, datetime, timedelta

    account = await accounts_repo.create(db_session, email="since-billing@example.com")
    await db_session.commit()

    # Billable L2 → credits=1
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://ok.com/1",
        layer=2,
        success=True,
        credits_used=1,
    )
    # Billable L3 → credits=2
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://ok.com/2",
        layer=3,
        success=True,
        credits_used=2,
    )
    # Failed → credits=0 (NOT billable)
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://fail.com",
        layer=2,
        success=False,
        credits_used=0,
    )
    await db_session.commit()

    since = datetime.now(UTC) - timedelta(hours=1)
    total = await usage_repo.sum_credits_since(db_session, account.id, since)
    assert total == 3  # 1 + 2, ignoring credits=0 rows


@pytest.mark.asyncio
async def test_list_requests_paginated(db_session: AsyncSession) -> None:
    """list_requests() trả về paginated results với filters."""
    account = await accounts_repo.create(db_session, email="paginated@example.com")
    await db_session.commit()

    # Tạo 10 requests với different layers và success status
    for i in range(10):
        await usage_repo.insert_record(
            db_session,
            account_id=account.id,
            api_key_id=None,
            url=f"https://example{i}.com/page",
            layer=(i % 3) + 1,  # 1, 2, 3, 1, 2, 3...
            success=(i % 2 == 0),  # alternating
            credits_used=1,
            request_id=f"req_{i:03d}",
            domain=f"example{i}.com",
            response_time_ms=100 * (i + 1),
            validation_valid=(i % 2 == 0),
        )
    await db_session.commit()

    # Test basic pagination - limit 5, offset 0
    result = await usage_repo.list_requests(
        db_session, account_id=account.id, limit=5, offset=0
    )
    assert len(result["requests"]) == 5
    assert result["total"] == 10
    # Kiểm tra fields trả về
    first = result["requests"][0]
    assert "request_id" in first
    assert "url" in first
    assert "layer" in first
    assert "success" in first

    # Test offset
    result2 = await usage_repo.list_requests(
        db_session, account_id=account.id, limit=5, offset=5
    )
    assert len(result2["requests"]) == 5
    assert result2["total"] == 10
    # Đảm bảo không trùng
    ids1 = {r["request_id"] for r in result["requests"]}
    ids2 = {r["request_id"] for r in result2["requests"]}
    assert ids1.isdisjoint(ids2)


@pytest.mark.asyncio
async def test_list_requests_filter_by_layer(db_session: AsyncSession) -> None:
    """list_requests() filter theo layer."""
    account = await accounts_repo.create(db_session, email="filter-layer@example.com")
    await db_session.commit()

    await usage_repo.insert_record(
        db_session, account_id=account.id, api_key_id=None,
        url="https://l1.com", layer=1, success=True, request_id="req_l1"
    )
    await usage_repo.insert_record(
        db_session, account_id=account.id, api_key_id=None,
        url="https://l2.com", layer=2, success=True, request_id="req_l2"
    )
    await usage_repo.insert_record(
        db_session, account_id=account.id, api_key_id=None,
        url="https://l3.com", layer=3, success=True, request_id="req_l3"
    )
    await db_session.commit()

    result = await usage_repo.list_requests(
        db_session, account_id=account.id, limit=50, offset=0, layer=2
    )
    assert result["total"] == 1
    assert result["requests"][0]["layer"] == 2


@pytest.mark.asyncio
async def test_list_requests_filter_by_success(db_session: AsyncSession) -> None:
    """list_requests() filter theo success status."""
    account = await accounts_repo.create(db_session, email="filter-success@example.com")
    await db_session.commit()

    await usage_repo.insert_record(
        db_session, account_id=account.id, api_key_id=None,
        url="https://ok.com", layer=2, success=True, request_id="req_ok"
    )
    await usage_repo.insert_record(
        db_session, account_id=account.id, api_key_id=None,
        url="https://fail.com", layer=2, success=False, request_id="req_fail"
    )
    await db_session.commit()

    result = await usage_repo.list_requests(
        db_session, account_id=account.id, limit=50, offset=0, success=True
    )
    assert result["total"] == 1
    assert result["requests"][0]["success"] is True

    result = await usage_repo.list_requests(
        db_session, account_id=account.id, limit=50, offset=0, success=False
    )
    assert result["total"] == 1
    assert result["requests"][0]["success"] is False


@pytest.mark.asyncio
async def test_list_requests_account_isolation(db_session: AsyncSession) -> None:
    """list_requests() chỉ trả về requests của account đó."""
    acc1 = await accounts_repo.create(db_session, email="acc1@example.com")
    acc2 = await accounts_repo.create(db_session, email="acc2@example.com")
    await db_session.commit()

    await usage_repo.insert_record(
        db_session, account_id=acc1.id, api_key_id=None,
        url="https://acc1.com", layer=1, success=True, request_id="req_acc1"
    )
    await usage_repo.insert_record(
        db_session, account_id=acc2.id, api_key_id=None,
        url="https://acc2.com", layer=1, success=True, request_id="req_acc2"
    )
    await db_session.commit()

    result = await usage_repo.list_requests(
        db_session, account_id=acc1.id, limit=50, offset=0
    )
    assert result["total"] == 1
    assert result["requests"][0]["request_id"] == "req_acc1"
