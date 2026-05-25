# -*- coding: utf-8 -*-
"""Unit tests cho budget cap logic — dùng SQLite in-memory."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from datask_api.db.repositories import accounts as accounts_repo
from datask_api.db.repositories import usage as usage_repo


@pytest.mark.asyncio
async def test_update_budget_sets_cap(db_session: AsyncSession) -> None:
    """update_budget() sets monthly_credit_budget and alert_threshold."""
    account = await accounts_repo.create(db_session, email="budget@example.com")
    await db_session.commit()

    await accounts_repo.update_budget(
        db_session,
        account_id=account.id,
        monthly_credit_budget=5000,
        budget_alert_threshold=80,
    )
    await db_session.commit()

    updated = await accounts_repo.get_by_id(db_session, account.id)
    assert updated is not None
    assert updated.monthly_credit_budget == 5000
    assert updated.budget_alert_threshold == 80


@pytest.mark.asyncio
async def test_update_budget_null_unlimited(db_session: AsyncSession) -> None:
    """Setting budget to NULL means unlimited PAYG."""
    account = await accounts_repo.create(db_session, email="unlimited@example.com")
    await db_session.commit()

    await accounts_repo.update_budget(
        db_session,
        account_id=account.id,
        monthly_credit_budget=5000,
    )
    await db_session.commit()

    await accounts_repo.update_budget(
        db_session,
        account_id=account.id,
        monthly_credit_budget=None,
    )
    await db_session.commit()

    updated = await accounts_repo.get_by_id(db_session, account.id)
    assert updated is not None
    assert updated.monthly_credit_budget is None


@pytest.mark.asyncio
async def test_budget_check_under_limit(db_session: AsyncSession) -> None:
    """Budget check passes when usage is below cap."""
    account = await accounts_repo.create(db_session, email="under@example.com")
    await db_session.commit()

    await accounts_repo.update_budget(
        db_session,
        account_id=account.id,
        monthly_credit_budget=100,
    )
    await db_session.commit()

    # Use 99 credits
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://example.com",
        layer=2,
        success=True,
        credits_used=99,
    )
    await db_session.commit()

    # Direct check via repo
    used = await usage_repo.sum_credits_current_month(db_session, account.id)
    assert used == 99

    updated = await accounts_repo.get_by_id(db_session, account.id)
    assert updated is not None
    assert used < updated.monthly_credit_budget


@pytest.mark.asyncio
async def test_budget_check_at_limit(db_session: AsyncSession) -> None:
    """Budget check fails when usage equals cap (100th credit → blocked)."""
    account = await accounts_repo.create(db_session, email="atlimit@example.com")
    await db_session.commit()

    await accounts_repo.update_budget(
        db_session,
        account_id=account.id,
        monthly_credit_budget=100,
    )
    await db_session.commit()

    # Use exactly 100 credits
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://example.com",
        layer=2,
        success=True,
        credits_used=99,
    )
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://example.com/2",
        layer=2,
        success=True,
        credits_used=1,
    )
    await db_session.commit()

    used = await usage_repo.sum_credits_current_month(db_session, account.id)
    assert used == 100

    updated = await accounts_repo.get_by_id(db_session, account.id)
    assert updated is not None
    assert used >= updated.monthly_credit_budget


@pytest.mark.asyncio
async def test_budget_check_over_limit(db_session: AsyncSession) -> None:
    """Budget check fails when usage exceeds cap."""
    account = await accounts_repo.create(db_session, email="over@example.com")
    await db_session.commit()

    await accounts_repo.update_budget(
        db_session,
        account_id=account.id,
        monthly_credit_budget=50,
    )
    await db_session.commit()

    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://example.com",
        layer=3,
        success=True,
        credits_used=51,
    )
    await db_session.commit()

    used = await usage_repo.sum_credits_current_month(db_session, account.id)
    assert used == 51

    updated = await accounts_repo.get_by_id(db_session, account.id)
    assert updated is not None
    assert used > updated.monthly_credit_budget


@pytest.mark.asyncio
async def test_budget_null_no_cap(db_session: AsyncSession) -> None:
    """Account with NULL budget has no cap (unlimited PAYG)."""
    account = await accounts_repo.create(db_session, email="nocap@example.com")
    await db_session.commit()

    updated = await accounts_repo.get_by_id(db_session, account.id)
    assert updated is not None
    assert updated.monthly_credit_budget is None


@pytest.mark.asyncio
async def test_budget_only_charges_billable(db_session: AsyncSession) -> None:
    """Budget check only counts billable credits (credits_used > 0)."""
    account = await accounts_repo.create(db_session, email="billable@example.com")
    await db_session.commit()

    await accounts_repo.update_budget(
        db_session,
        account_id=account.id,
        monthly_credit_budget=100,
    )
    await db_session.commit()

    # Failed jobs should have credits_used=0 (not billable)
    for _ in range(50):
        await usage_repo.insert_record(
            db_session,
            account_id=account.id,
            api_key_id=None,
            url="https://fail.com",
            layer=2,
            success=False,
            credits_used=0,
        )

    # Only 99 billable credits
    await usage_repo.insert_record(
        db_session,
        account_id=account.id,
        api_key_id=None,
        url="https://ok.com",
        layer=2,
        success=True,
        credits_used=99,
    )
    await db_session.commit()

    used = await usage_repo.sum_credits_current_month(db_session, account.id)
    assert used == 99

    updated = await accounts_repo.get_by_id(db_session, account.id)
    assert updated is not None
    assert used < updated.monthly_credit_budget


@pytest.mark.asyncio
async def test_budget_default_threshold(db_session: AsyncSession) -> None:
    """Default budget_alert_threshold is 80."""
    account = await accounts_repo.create(db_session, email="threshold@example.com")
    await db_session.commit()

    assert account.budget_alert_threshold == 80


@pytest.mark.asyncio
async def test_budget_custom_threshold(db_session: AsyncSession) -> None:
    """Custom budget_alert_threshold is stored correctly."""
    account = await accounts_repo.create(db_session, email="custom-thresh@example.com")
    await db_session.commit()

    await accounts_repo.update_budget(
        db_session,
        account_id=account.id,
        monthly_credit_budget=5000,
        budget_alert_threshold=90,
    )
    await db_session.commit()

    updated = await accounts_repo.get_by_id(db_session, account.id)
    assert updated is not None
    assert updated.budget_alert_threshold == 90
