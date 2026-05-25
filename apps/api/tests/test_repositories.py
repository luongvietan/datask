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
