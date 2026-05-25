# -*- coding: utf-8 -*-
"""
Layer 1 — GET /v1/fetch?url={url}
Free, no auth required. Rate-limited by IP.
Optional: pass Authorization header for better rate limits and usage tracking.
"""
from datask_core.models import ErrorCode, ErrorResponse, FetchResponse
from fastapi import APIRouter, Header, Query, Request
from fastapi.responses import JSONResponse

from datask_api.services.job_queue import enqueue_fetch_job
from datask_api.services.rate_limiter import check_ip_rate_limit

router = APIRouter()


def _get_client_ip(request: Request) -> str:
    """Extract real client IP, respecting X-Forwarded-For from trusted proxies."""
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get(
    "/fetch",
    response_model=FetchResponse,
    responses={
        429: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Fetch clean content from any URL (free, no auth required)",
)
async def fetch_url(
    request: Request,
    url: str = Query(..., description="URL to fetch"),
    authorization: str | None = Header(default=None),
) -> FetchResponse | JSONResponse:
    # Validate URL before consuming rate limit budget
    if not url.startswith(("http://", "https://")):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error=ErrorCode.INVALID_URL,
                message="URL must start with http:// or https://",
            ).model_dump(),
        )

    client_ip = _get_client_ip(request)
    allowed, retry_after = await check_ip_rate_limit(client_ip)
    if not allowed:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(retry_after), "X-RateLimit-Remaining": "0"},
            content=ErrorResponse(
                error=ErrorCode.RATE_LIMITED,
                message="Rate limit exceeded. Please slow down.",
                retry_after=retry_after,
            ).model_dump(),
        )

    # Optional auth — for tracking usage if user provides API key
    account_id = None
    api_key_id = None
    if authorization and authorization.startswith("Bearer "):
        raw_key = authorization[7:]
        if raw_key.startswith("dtsk_live_"):
            try:
                from datask_api.services.api_keys import validate_api_key
                key_record = await validate_api_key(raw_key)
                if key_record:
                    account_id = key_record["account_id"]
                    api_key_id = key_record["id"]
            except Exception:
                pass

    try:
        result = await enqueue_fetch_job(url=url, account_id=account_id, api_key_id=api_key_id)
        return result
    except (ConnectionError, OSError) as exc:
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error=ErrorCode.INTERNAL_ERROR,
                message="Worker unavailable. Redis is not running — start Redis to enable scraping.",
            ).model_dump(),
        )
    except TimeoutError:
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error=ErrorCode.INTERNAL_ERROR,
                message="Fetch timed out after 30s. The site may be slow or blocking requests.",
            ).model_dump(),
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=ErrorCode.INTERNAL_ERROR,
                message=f"Fetch failed: {exc}",
            ).model_dump(),
        )
