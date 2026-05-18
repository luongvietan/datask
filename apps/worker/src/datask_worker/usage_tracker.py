# -*- coding: utf-8 -*-
"""
Usage tracking helper cho worker.
Ghi UsageRecord vào PostgreSQL sau mỗi job.
"""
import structlog
from datetime import UTC, datetime

from datask_worker.db import get_session

logger = structlog.get_logger()


def record_usage(
    account_id: str | None,
    api_key_id: str | None,
    url: str,
    layer: int,
    success: bool,
    credits_used: int = 1,
    response_time_ms: int | None = None,
    error_code: str | None = None,
) -> None:
    """
    Ghi usage record. Fire-and-forget — lỗi không làm fail job.
    account_id=None cho Layer 1 anonymous requests.
    """
    if account_id is None:
        # Layer 1 anonymous — bỏ qua (không track)
        return

    try:
        from datask_api.models.db import UsageRecord  # type: ignore[import]

        with get_session() as session:
            record = UsageRecord(
                account_id=account_id,
                api_key_id=api_key_id,
                url=url,
                layer=layer,
                success=success,
                credits_used=credits_used,
                response_time_ms=response_time_ms,
                error_code=error_code,
            )
            session.add(record)

        logger.debug(
            "usage_recorded",
            account_id=account_id,
            layer=layer,
            success=success,
            credits_used=credits_used,
        )
    except Exception as e:
        # Không raise — usage tracking failure không nên fail job
        logger.error("usage_record_failed", error=str(e), account_id=account_id)
