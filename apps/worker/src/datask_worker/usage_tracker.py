# -*- coding: utf-8 -*-
"""
Usage tracking helper cho worker.
Ghi UsageRecord vào PostgreSQL sau mỗi job.
"""
from __future__ import annotations

import structlog
from urllib.parse import urlparse

from sqlalchemy.exc import IntegrityError

from datask_worker.db import get_session

logger = structlog.get_logger()


_LAYER_CREDITS = {1: 1, 2: 1, 3: 2}


def compute_credits(
    success: bool,
    validation_valid: bool | None,
    layer: int,
) -> int:
    """
    Success-only billing: chỉ charge credits khi job thành công
    VÀ validation không fail (nếu có validation).
    """
    if not success:
        return 0
    if validation_valid is False:
        return 0
    return _LAYER_CREDITS.get(layer, 1)


def _extract_domain(url: str) -> str | None:
    try:
        netloc = urlparse(url).netloc or None
        if netloc and len(netloc) > 256:
            return netloc[:256]
        return netloc
    except Exception:
        return None


def record_usage(
    account_id: str | None,
    api_key_id: str | None,
    url: str,
    layer: int,
    success: bool,
    credits_used: int = 0,
    response_time_ms: int | None = None,
    error_code: str | None = None,
    request_id: str | None = None,
    validation_valid: bool | None = None,
    model: str | None = None,
    fetch_strategy: str | None = None,
    cache_hit: bool = False,
    metadata: dict | None = None,
) -> None:
    """
    Ghi usage record. Fire-and-forget — lỗi không làm fail job.
    account_id=None cho Layer 1 anonymous requests.
    """
    if account_id is None:
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
                request_id=request_id,
                domain=_extract_domain(url),
                validation_valid=validation_valid,
                model=model,
                fetch_strategy=fetch_strategy,
                cache_hit=cache_hit,
                metadata_=metadata,
            )
            session.add(record)

        logger.debug(
            "usage_recorded",
            account_id=account_id,
            layer=layer,
            success=success,
            credits_used=credits_used,
            request_id=request_id,
        )
    except IntegrityError:
        logger.warning(
            "usage_record_duplicate",
            account_id=account_id,
            request_id=request_id,
        )
    except Exception as e:
        logger.error("usage_record_failed", error=str(e), account_id=account_id, request_id=request_id)
