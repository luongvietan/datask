# -*- coding: utf-8 -*-
"""Repository cho bảng usage_records."""
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from datask_api.models.db import UsageRecord
from sqlalchemy import Integer, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def insert_record(
    session: AsyncSession,
    account_id: str,
    api_key_id: str | None,
    url: str,
    layer: int,
    success: bool,
    credits_used: int = 1,
    response_time_ms: int | None = None,
    error_code: str | None = None,
    request_id: str | None = None,
    domain: str | None = None,
    validation_valid: bool | None = None,
    model: str | None = None,
    fetch_strategy: str | None = None,
    cache_hit: bool = False,
    metadata: dict[str, Any] | None = None,
) -> UsageRecord:
    record = UsageRecord(
        account_id=account_id,
        api_key_id=api_key_id,
        url=url,
        layer=layer,
        success=success,
        credits_used=credits_used,
        response_time_ms=response_time_ms,
        error_code=error_code,
        request_id=request_id,
        domain=domain,
        validation_valid=validation_valid,
        model=model,
        fetch_strategy=fetch_strategy,
        cache_hit=cache_hit,
        metadata_=metadata,
    )
    session.add(record)
    await session.flush()
    return record


async def count_current_month(session: AsyncSession, account_id: str) -> int:
    """Đếm số request thành công trong tháng hiện tại."""
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    result = await session.execute(
        select(func.count(UsageRecord.id)).where(
            UsageRecord.account_id == account_id,
            UsageRecord.success == True,  # noqa: E712
            UsageRecord.created_at >= month_start,
        )
    )
    return result.scalar_one() or 0


async def sum_credits_current_month(session: AsyncSession, account_id: str) -> int:
    """Tổng credits dùng trong tháng hiện tại (chỉ tính billable requests)."""
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    result = await session.execute(
        select(func.coalesce(func.sum(UsageRecord.credits_used), 0)).where(
            UsageRecord.account_id == account_id,
            UsageRecord.created_at >= month_start,
            UsageRecord.credits_used > 0,
        )
    )
    return result.scalar_one() or 0


async def get_summary(session: AsyncSession, account_id: str) -> dict[str, Any]:
    """Lấy usage summary cho tháng hiện tại."""
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    result = await session.execute(
        select(
            func.count(UsageRecord.id).label("total"),
            func.sum(
                case((UsageRecord.success == True, 1), else_=0)  # noqa: E712
            ).label("successful"),
            func.coalesce(
                func.sum(
                    case((UsageRecord.credits_used > 0, UsageRecord.credits_used), else_=0)
                ),
                0,
            ).label("credits"),
        ).where(
            UsageRecord.account_id == account_id,
            UsageRecord.created_at >= month_start,
        )
    )
    row = result.one()
    total = row.total or 0
    successful = int(row.successful or 0)
    credits = int(row.credits or 0)
    return {
        "current_month_requests": total,
        "successful_requests": successful,
        "failed_requests": total - successful,
        "credits_used": credits,
    }


async def top_domains(
    session: AsyncSession, account_id: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Top domains theo số request trong tháng hiện tại."""
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    result = await session.execute(
        select(UsageRecord.url, func.count(UsageRecord.id).label("count")).where(
            UsageRecord.account_id == account_id,
            UsageRecord.created_at >= month_start,
        )
        .group_by(UsageRecord.url)
        .order_by(func.count(UsageRecord.id).desc())
        .limit(limit * 5)  # fetch more, aggregate by domain in Python
    )
    rows = result.all()

    domain_counts: dict[str, int] = {}
    for row in rows:
        try:
            domain = urlparse(row.url).netloc or row.url
        except Exception:
            domain = row.url
        domain_counts[domain] = domain_counts.get(domain, 0) + row.count

    sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"domain": d, "count": c} for d, c in sorted_domains[:limit]]


async def sum_credits_since(session: AsyncSession, account_id: str, since: datetime) -> int:
    """Tổng billable credits từ thời điểm `since` đến nay (cho Stripe metered billing)."""
    result = await session.execute(
        select(func.coalesce(func.sum(UsageRecord.credits_used), 0)).where(
            UsageRecord.account_id == account_id,
            UsageRecord.created_at >= since,
            UsageRecord.credits_used > 0,
        )
    )
    return result.scalar_one() or 0
