# -*- coding: utf-8 -*-
"""
Layer 2/3 — POST /v1/extract
Requires API key. Layer 2 = schema, Layer 3 = prompt.
"""
from datask_core.config import get_settings
from datask_core.models import ErrorCode, ErrorResponse, ExtractRequest, ExtractResponse
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from datask_api.middleware.auth import get_current_key
from datask_api.services.job_queue import enqueue_extract_job
from datask_api.services.rate_limiter import TIER_BURST_PER_MINUTE, check_key_rate_limit, get_remaining
from datask_api.db.repositories import usage as usage_repo
from datask_api.db.session import get_session_factory

router = APIRouter()


@router.post(
    "/extract",
    response_model=ExtractResponse,
    responses={
        401: {"model": ErrorResponse},
        402: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Extract structured data from a URL (API key required)",
)
async def extract_url(
    request: Request,
    payload: ExtractRequest,
    api_key_record=Depends(get_current_key),  # noqa: B008
) -> ExtractResponse | JSONResponse:
    settings = get_settings()
    key_id = api_key_record["id"]
    account_id = api_key_record["account_id"]
    tier = api_key_record.get("tier", "free")

    # Rate limit check
    allowed, retry_after = await check_key_rate_limit(key_id, tier=tier)

    if not allowed:
        limit = TIER_BURST_PER_MINUTE.get(tier, TIER_BURST_PER_MINUTE["free"])
        return JSONResponse(
            status_code=429,
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Limit": str(limit),
            },
            content=ErrorResponse(
                error=ErrorCode.RATE_LIMITED,
                message="Rate limit exceeded.",
                retry_after=retry_after,
            ).model_dump(),
        )

    # payload.url already validated by Pydantic model — no duplicate check needed

    if payload.mode is None:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error=ErrorCode.INVALID_SCHEMA,
                message="Request must include either 'schema' (Layer 2) or 'prompt' (Layer 3).",
            ).model_dump(),
        )

    # Monthly quota check for free tier
    if tier == "free":
        factory = get_session_factory()
        async with factory() as session:
            current_count = await usage_repo.count_current_month(session, account_id)

        if current_count >= settings.free_tier_monthly_quota:
            return JSONResponse(
                status_code=402,
                content=ErrorResponse(
                    error=ErrorCode.QUOTA_EXCEEDED,
                    message=f"Free tier monthly quota of {settings.free_tier_monthly_quota} requests exceeded.",
                    upgrade_url=f"{settings.base_url}/pricing",
                ).model_dump(),
            )

    remaining = await get_remaining(key_id, tier=tier)
    limit = TIER_BURST_PER_MINUTE.get(tier, TIER_BURST_PER_MINUTE["free"])

    # Check if async mode requested
    is_async = request.headers.get("X-Datask-Async", "").lower() in ("true", "1", "yes")

    try:
        result = await enqueue_extract_job(
            url=payload.url,
            mode=payload.mode,
            schema=payload.schema_,
            prompt=payload.prompt,
            example=payload.example,
            api_key_id=key_id,
            account_id=account_id,
            is_async=is_async,
        )
    except (ConnectionError, OSError):
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error=ErrorCode.INTERNAL_ERROR,
                message="Worker unavailable. Redis is not running — start Redis to enable extraction.",
            ).model_dump(),
        )
    except TimeoutError:
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error=ErrorCode.INTERNAL_ERROR,
                message="Extraction timed out after 60s.",
            ).model_dump(),
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=ErrorCode.INTERNAL_ERROR,
                message=f"Extraction failed: {exc}",
            ).model_dump(),
        )

    if isinstance(result, JSONResponse):
        return result

    response = JSONResponse(
        status_code=200,
        content=result.model_dump(mode="json"),
        headers={
            "X-RateLimit-Remaining": str(max(0, remaining - 1)),
            "X-RateLimit-Limit": str(limit),
        },
    )
    return response
