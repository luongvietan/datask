# -*- coding: utf-8 -*-
"""
Job queue service — enqueue fetch/extract jobs to RQ workers.
Uses Redis as broker. Workers run in apps/worker/.
"""
import asyncio
import time
from typing import Any

import redis
import redis.asyncio as aioredis
from datask_core.config import get_settings
from datask_core.models import ExtractionMode, ExtractResponse, FetchResponse
from fastapi.responses import JSONResponse
from rq import Queue
from rq.job import Job

_queue: Queue | None = None
_redis_async: aioredis.Redis | None = None


def _get_queue() -> Queue:
    global _queue
    if _queue is None:
        settings = get_settings()
        conn = redis.from_url(settings.redis_url)
        _queue = Queue("datask", connection=conn)
    return _queue


async def _get_async_redis() -> aioredis.Redis:
    global _redis_async
    if _redis_async is None:
        settings = get_settings()
        _redis_async = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_async


async def enqueue_fetch_job(
    url: str,
    account_id: str | None = None,
    api_key_id: str | None = None,
    request_id: str | None = None,
) -> FetchResponse:
    """
    Enqueue Layer 1 fetch job và chờ kết quả.
    RQ calls are sync — offloaded to thread executor to avoid blocking event loop.
    Timeout 30s.
    """
    q = await asyncio.to_thread(_get_queue)
    job: Job = await asyncio.to_thread(
        q.enqueue,
        "datask_worker.tasks.fetch.run_fetch",
        url,
        account_id,
        api_key_id,
        request_id,
        job_timeout=30,
        result_ttl=120,
    )

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        await asyncio.to_thread(job.refresh)
        if job.is_finished:
            result = job.result
            if isinstance(result, dict):
                return FetchResponse(**result)
            return result
        if job.is_failed:
            raise ValueError(f"Worker job failed: {job.exc_info}")
        await asyncio.sleep(0.2)

    raise TimeoutError("Fetch job timed out after 30s")


async def enqueue_extract_job(
    url: str,
    mode: ExtractionMode,
    schema: dict[str, Any] | None,
    prompt: str | None,
    example: dict[str, Any] | None,
    api_key_id: str,
    account_id: str,
    is_async: bool = False,
    request_id: str | None = None,
) -> ExtractResponse | JSONResponse:
    """
    Enqueue Layer 2/3 extract job.
    is_async=True: trả 202 ngay với job_id.
    is_async=False: chờ tối đa 60s.
    """
    q = await asyncio.to_thread(_get_queue)
    job: Job = await asyncio.to_thread(
        q.enqueue,
        "datask_worker.tasks.extract.run_extract",
        url,
        mode.value,
        schema,
        prompt,
        example,
        api_key_id,
        account_id,
        request_id,
        job_timeout=60,
        result_ttl=300,
    )

    if is_async:
        return JSONResponse(
            status_code=202,
            content={
                "job_id": job.id,
                "status": "queued",
                "status_url": f"/v1/jobs/{job.id}",
                "meta": {"request_id": request_id},
            },
        )

    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        await asyncio.to_thread(job.refresh)
        if job.is_finished:
            result = job.result
            if isinstance(result, dict):
                return ExtractResponse(**result)
            return result
        if job.is_failed:
            raise ValueError(f"Worker job failed: {job.exc_info}")
        await asyncio.sleep(0.3)

    raise TimeoutError("Extract job timed out after 60s")


async def get_job_status(job_id: str) -> dict[str, Any] | None:
    """Poll job status từ RQ."""
    try:
        q = await asyncio.to_thread(_get_queue)
        job: Job = await asyncio.to_thread(Job.fetch, job_id, connection=q.connection)
        await asyncio.to_thread(job.refresh)

        status = "queued"
        result = None

        if job.is_queued:
            status = "queued"
        elif job.is_started:
            status = "processing"
        elif job.is_finished:
            status = "completed"
            result = job.result
        elif job.is_failed:
            status = "failed"

        return {
            "job_id": job_id,
            "status": status,
            "result": result,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
    except Exception:
        return None
