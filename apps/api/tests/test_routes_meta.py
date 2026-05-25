# -*- coding: utf-8 -*-
"""API route tests — meta.request_id on fetch/extract responses."""
from unittest.mock import AsyncMock, patch

from datask_api.middleware.auth import get_current_key
from datask_api.middleware.request_context import REQUEST_ID_HEADER, RequestContextMiddleware
from datask_api.routes import extract, fetch
from datask_core.models import (
    ContentType,
    ExtractResponse,
    FetchResponse,
    OutputValidationResult,
    RequestMeta,
    ValidationError,
)
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient


def _sample_meta() -> RequestMeta:
    return RequestMeta(
        request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
        layer=1,
        latency_ms=120,
        fetch_strategy="async",
        cache_hit=False,
    )


def _make_fetch_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)
    app.include_router(fetch.router, prefix="/v1")
    return app


def _make_extract_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)
    app.include_router(extract.router, prefix="/v1")

    async def fake_key() -> dict[str, str]:
        return {"id": "key-1", "account_id": "acc-1", "tier": "pro"}

    app.dependency_overrides[get_current_key] = fake_key
    return app


async def test_fetch_success_includes_meta_request_id():
    app = _make_fetch_app()
    mock_response = FetchResponse(
        content="# Hello",
        url="https://example.com",
        content_type=ContentType.MARKDOWN,
        meta=_sample_meta(),
    )

    with patch("datask_api.routes.fetch.check_ip_rate_limit", new_callable=AsyncMock) as mock_rl:
        mock_rl.return_value = (True, 0)
        with patch(
            "datask_api.routes.fetch.enqueue_fetch_job",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/v1/fetch", params={"url": "https://example.com"})

    assert response.status_code == 200
    assert response.json()["meta"]["request_id"].startswith("req_")
    assert response.headers.get(REQUEST_ID_HEADER) is not None


async def test_fetch_invalid_url_still_has_request_id_header():
    app = _make_fetch_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/fetch", params={"url": "ftp://bad.com"})

    assert response.status_code == 422
    header = response.headers.get(REQUEST_ID_HEADER)
    assert header is not None
    assert header.startswith("req_")


async def test_fetch_rate_limited_still_has_request_id_header():
    app = _make_fetch_app()

    with patch("datask_api.routes.fetch.check_ip_rate_limit", new_callable=AsyncMock) as mock_rl:
        mock_rl.return_value = (False, 30)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/v1/fetch", params={"url": "https://example.com"})

    assert response.status_code == 429
    assert response.headers.get(REQUEST_ID_HEADER) is not None


async def test_extract_sync_response_includes_validation_block_when_invalid():
    app = _make_extract_app()
    mock_response = ExtractResponse(
        data={"price": "bad"},
        url="https://example.com",
        validation=OutputValidationResult(
            valid=False,
            errors=[
                ValidationError(
                    field="price",
                    code="type_mismatch",
                    message="Field 'price' expected type 'number', got str",
                )
            ],
        ),
        meta=RequestMeta(
            request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
            layer=2,
            latency_ms=500,
        ),
    )

    with patch("datask_api.routes.extract.check_key_rate_limit", new_callable=AsyncMock) as mock_rl:
        mock_rl.return_value = (True, 0)
        with patch("datask_api.routes.extract.get_remaining", new_callable=AsyncMock) as mock_rem:
            mock_rem.return_value = 10
            with patch(
                "datask_api.routes.extract.enqueue_extract_job",
                new_callable=AsyncMock,
                return_value=mock_response,
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/v1/extract",
                        json={"url": "https://example.com", "schema": {"price": "number"}},
                        headers={"Authorization": "Bearer dtsk_live_test"},
                    )

    assert response.status_code == 200
    body = response.json()
    assert body["validation"]["valid"] is False
    assert body["validation"]["errors"][0]["code"] == "type_mismatch"
    assert body["validation"]["errors"][0]["field"] == "price"


async def test_extract_sync_success_includes_meta_request_id():
    app = _make_extract_app()
    mock_response = ExtractResponse(
        data={"title": "Widget"},
        url="https://example.com",
        meta=RequestMeta(
            request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
            layer=2,
            latency_ms=500,
        ),
    )

    with patch("datask_api.routes.extract.check_key_rate_limit", new_callable=AsyncMock) as mock_rl:
        mock_rl.return_value = (True, 0)
        with patch("datask_api.routes.extract.get_remaining", new_callable=AsyncMock) as mock_rem:
            mock_rem.return_value = 10
            with patch(
                "datask_api.routes.extract.enqueue_extract_job",
                new_callable=AsyncMock,
                return_value=mock_response,
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/v1/extract",
                        json={"url": "https://example.com", "schema": {"title": "string"}},
                        headers={"Authorization": "Bearer dtsk_live_test"},
                    )

    assert response.status_code == 200
    assert response.json()["meta"]["request_id"].startswith("req_")


async def test_extract_invalid_schema_returns_400_before_enqueue():
    app = _make_extract_app()

    with patch("datask_api.routes.extract.check_key_rate_limit", new_callable=AsyncMock) as mock_rl:
        with patch(
            "datask_api.routes.extract.enqueue_extract_job",
            new_callable=AsyncMock,
        ) as mock_enqueue:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/v1/extract",
                    json={"url": "https://example.com", "schema": {"price": "currency"}},
                    headers={"Authorization": "Bearer dtsk_live_test"},
                )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "invalid_schema"
    mock_rl.assert_not_called()
    mock_enqueue.assert_not_called()


async def test_extract_invalid_schema_list_type_returns_400():
    app = _make_extract_app()

    with patch("datask_api.routes.extract.check_key_rate_limit", new_callable=AsyncMock) as mock_rl:
        with patch(
            "datask_api.routes.extract.enqueue_extract_job",
            new_callable=AsyncMock,
        ) as mock_enqueue:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/v1/extract",
                    json={"url": "https://example.com", "schema": {"price": ["number"]}},
                    headers={"Authorization": "Bearer dtsk_live_test"},
                )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_schema"
    mock_rl.assert_not_called()
    mock_enqueue.assert_not_called()


async def test_extract_invalid_schema_missing_type_returns_400():
    app = _make_extract_app()

    with patch("datask_api.routes.extract.check_key_rate_limit", new_callable=AsyncMock) as mock_rl:
        with patch(
            "datask_api.routes.extract.enqueue_extract_job",
            new_callable=AsyncMock,
        ) as mock_enqueue:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/v1/extract",
                    json={"url": "https://example.com", "schema": {"price": {"required": True}}},
                    headers={"Authorization": "Bearer dtsk_live_test"},
                )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_schema"
    mock_rl.assert_not_called()
    mock_enqueue.assert_not_called()


async def test_extract_async_202_includes_meta_request_id():
    app = _make_extract_app()
    async_response = JSONResponse(
        status_code=202,
        content={
            "job_id": "job-123",
            "status": "queued",
            "status_url": "/v1/jobs/job-123",
            "meta": {"request_id": "req_01JABCDEFGHJKMNPQRSTVWXYZ0"},
        },
    )

    with patch("datask_api.routes.extract.check_key_rate_limit", new_callable=AsyncMock) as mock_rl:
        mock_rl.return_value = (True, 0)
        with patch("datask_api.routes.extract.get_remaining", new_callable=AsyncMock) as mock_rem:
            mock_rem.return_value = 10
            with patch(
                "datask_api.routes.extract.enqueue_extract_job",
                new_callable=AsyncMock,
                return_value=async_response,
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/v1/extract",
                        json={"url": "https://example.com", "schema": {"title": "string"}},
                        headers={
                            "Authorization": "Bearer dtsk_live_test",
                            "X-Datask-Async": "true",
                        },
                    )

    assert response.status_code == 202
    assert response.json()["meta"]["request_id"].startswith("req_")
    assert response.headers.get(REQUEST_ID_HEADER) is not None
