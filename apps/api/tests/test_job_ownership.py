# -*- coding: utf-8 -*-
"""Tests for job poll account ownership — Story 2.3"""
from unittest.mock import AsyncMock, patch

from datask_api.middleware.auth import get_current_key
from datask_api.routes import jobs
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def _make_app(account_id: str) -> FastAPI:
    """Create test app with mocked auth returning specific account_id."""
    app = FastAPI()
    app.include_router(jobs.router, prefix="/v1")

    async def fake_key() -> dict:
        return {
            "id": "key-test",
            "account_id": account_id,
            "tier": "pro",
            "label": "test-key",
            "key_prefix": "dtsk_live_",
            "is_active": True,
            "stripe_subscription_id": None,
            "is_session": False,
        }

    app.dependency_overrides[get_current_key] = fake_key
    return app


async def test_job_poll_owner_success():
    """Owner can poll their own job — returns 200 with job status."""
    app = _make_app(account_id="acc-owner-123")

    mock_status = {
        "job_id": "job-xyz",
        "status": "completed",
        "result": {"data": "extracted"},
        "created_at": "2026-05-26T03:00:00",
        "meta": {"account_id": "acc-owner-123", "request_id": "req-abc"},
    }

    with patch("datask_api.routes.jobs.get_job_status", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_status
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/v1/jobs/job-xyz")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["result"] == {"data": "extracted"}
    assert "meta" not in body  # meta should be stripped from response


async def test_job_poll_wrong_account_returns_403():
    """Non-owner gets 403 (disguised as 'not found' to avoid leaking existence)."""
    app = _make_app(account_id="acc-attacker-456")

    mock_status = {
        "job_id": "job-xyz",
        "status": "completed",
        "result": {"data": "secret"},
        "created_at": "2026-05-26T03:00:00",
        "meta": {"account_id": "acc-owner-123", "request_id": "req-abc"},
    }

    with patch("datask_api.routes.jobs.get_job_status", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_status
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/v1/jobs/job-xyz")

    assert response.status_code == 403
    body = response.json()
    assert body["error"] == "internal_error"
    assert body["message"] == "Job not found."


async def test_job_poll_nonexistent_returns_404():
    """Unknown job_id returns 404."""
    app = _make_app(account_id="acc-anyone")

    with patch("datask_api.routes.jobs.get_job_status", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None  # job not found
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/v1/jobs/job-nonexistent")

    assert response.status_code == 404
    body = response.json()
    assert "not found" in body["message"].lower()


async def test_job_poll_missing_meta_returns_403():
    """Job without meta (legacy jobs) should be rejected for safety."""
    app = _make_app(account_id="acc-anyone")

    mock_status = {
        "job_id": "job-legacy",
        "status": "completed",
        "result": {"data": "legacy"},
        "created_at": "2026-05-26T03:00:00",
        "meta": {},  # no account_id in meta
    }

    with patch("datask_api.routes.jobs.get_job_status", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_status
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/v1/jobs/job-legacy")

    # Should be 403 because meta.account_id (None) != current account_id
    assert response.status_code == 403
