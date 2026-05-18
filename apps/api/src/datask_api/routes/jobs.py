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
    return JSONResponse(content=status)
