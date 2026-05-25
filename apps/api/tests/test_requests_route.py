# -*- coding: utf-8 -*-
"""Route tests cho GET /v1/requests — pagination + filters."""
from unittest.mock import AsyncMock, patch

from datask_api.middleware.auth import get_current_key
from datask_api.routes import requests as requests_router
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(requests_router.router, prefix="/v1")

    async def fake_key() -> dict:
        return {"id": "key-1", "account_id": "acc-test", "tier": "free"}

    app.dependency_overrides[get_current_key] = fake_key
    return app


async def test_list_requests_returns_paginated_data():
    app = _make_app()
    mock_result = {
        "requests": [
            {
                "request_id": "req_001",
                "url": "https://example.com/page",
                "domain": "example.com",
                "layer": 2,
                "success": True,
                "credits_used": 1,
                "response_time_ms": 120,
                "validation_valid": True,
                "created_at": "2026-05-25T10:00:00+00:00",
            }
        ],
        "total": 1,
    }

    with patch(
        "datask_api.routes.requests.get_session_factory"
    ) as mock_factory:
        mock_session = AsyncMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "datask_api.routes.requests.usage_repo.list_requests",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/v1/requests")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["requests"]) == 1
    assert body["requests"][0]["request_id"] == "req_001"


async def test_list_requests_requires_auth():
    app = FastAPI()
    app.include_router(requests_router.router, prefix="/v1")
    # No auth override → 401

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/requests")

    assert response.status_code == 401


async def test_list_requests_validates_limit():
    app = _make_app()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/requests", params={"limit": 0})

    assert response.status_code == 422


async def test_list_requests_validates_layer():
    app = _make_app()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/requests", params={"layer": 5})

    assert response.status_code == 422


async def test_list_requests_passes_query_params():
    app = _make_app()
    mock_result = {"requests": [], "total": 0}

    with patch(
        "datask_api.routes.requests.get_session_factory"
    ) as mock_factory:
        mock_session = AsyncMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "datask_api.routes.requests.usage_repo.list_requests",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_list:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/v1/requests",
                    params={"limit": 10, "offset": 5, "layer": 2, "success": True},
                )

    assert response.status_code == 200
    mock_list.assert_called_once()
    call_kwargs = mock_list.call_args.kwargs
    assert call_kwargs["limit"] == 10
    assert call_kwargs["offset"] == 5
    assert call_kwargs["layer"] == 2
    assert call_kwargs["success"] is True
    assert call_kwargs["account_id"] == "acc-test"
