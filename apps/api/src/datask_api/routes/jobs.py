# -*- coding: utf-8 -*-
"""
Async job polling — GET /v1/jobs/{job_id}
Dùng khi client gửi X-Datask-Async: true
"""
from datask_core.models import ErrorCode, ErrorResponse
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from datask_api.middleware.auth import get_current_key
from datask_api.services.job_queue import get_job_status

router = APIRouter()


@router.get(
    "/jobs/{job_id}",
    summary="Poll status of an async job",
    responses={
        404: {"model": ErrorResponse},
    },
)
async def poll_job(
    job_id: str,
    _current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    status = await get_job_status(job_id)
    if status is None:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error=ErrorCode.INTERNAL_ERROR,
                message=f"Job {job_id} not found.",
            ).model_dump(),
        )

    # Ownership check: job.meta.account_id must match current key's account_id
    job_account_id = status.get("meta", {}).get("account_id")
    current_account_id = _current_key.get("account_id")

    if job_account_id != current_account_id:
        return JSONResponse(
            status_code=403,
            content=ErrorResponse(
                error=ErrorCode.INTERNAL_ERROR,
                message="Job not found.",
            ).model_dump(),
        )

    # Remove meta from response (internal use only)
    response_data = {k: v for k, v in status.items() if k != "meta"}
    return JSONResponse(content=response_data)
