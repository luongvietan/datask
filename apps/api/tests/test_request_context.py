# -*- coding: utf-8 -*-
"""Tests cho request context middleware."""

from datask_core.request_id import REQUEST_ID_PATTERN, generate_request_id, is_valid_request_id
from datask_api.middleware.request_context import (
    REQUEST_ID_HEADER,
    RequestContextMiddleware,
    get_request_id,
    resolve_request_id,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient


def _make_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)

    @app.get("/ping")
    async def ping(request: Request) -> dict[str, str]:
        return {"request_id": get_request_id(request)}

    @app.get("/bad")
    async def bad() -> JSONResponse:
        return JSONResponse(status_code=422, content={"error": "invalid"})

    return app


async def test_middleware_adds_request_id_header():
    app = _make_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/ping")

    header = response.headers.get(REQUEST_ID_HEADER)
    assert header is not None
    assert REQUEST_ID_PATTERN.match(header)
    assert response.json()["request_id"] == header


async def test_middleware_preserves_valid_incoming_request_id():
    app = _make_app()
    incoming = generate_request_id()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/ping", headers={REQUEST_ID_HEADER: incoming})

    assert response.headers.get(REQUEST_ID_HEADER) == incoming
    assert response.json()["request_id"] == incoming


async def test_middleware_regenerates_invalid_incoming_request_id():
    app = _make_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/ping", headers={REQUEST_ID_HEADER: "req_not-a-ulid"})

    header = response.headers.get(REQUEST_ID_HEADER)
    assert header is not None
    assert header != "req_not-a-ulid"
    assert REQUEST_ID_PATTERN.match(header)


async def test_middleware_regenerates_oversized_incoming_request_id():
    oversized = "req_" + ("A" * 40)
    assert not is_valid_request_id(oversized)
    regenerated = resolve_request_id(oversized)
    assert REQUEST_ID_PATTERN.match(regenerated)


async def test_middleware_adds_header_on_error_response():
    app = _make_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/bad")

    assert response.status_code == 422
    header = response.headers.get(REQUEST_ID_HEADER)
    assert header is not None
    assert REQUEST_ID_PATTERN.match(header)