# -*- coding: utf-8 -*-
"""
Request context middleware — inject request_id vào mọi HTTP request/response.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable

from datask_core.request_id import generate_request_id, is_valid_request_id
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-Id"
REQUEST_ID_STATE_KEY = "request_id"


def resolve_request_id(incoming: str | None) -> str:
    """Accept client ID only when it matches req_{ulid}; otherwise generate server-side."""
    if incoming:
        candidate = incoming.strip()
        if is_valid_request_id(candidate):
            return candidate
    return generate_request_id()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Gán request_id duy nhất cho mỗi request và echo qua response header."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = resolve_request_id(request.headers.get(REQUEST_ID_HEADER))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def get_request_id(request: Request) -> str:
    """Lấy request_id từ request state; fallback generate nếu middleware chưa chạy."""
    existing = getattr(request.state, REQUEST_ID_STATE_KEY, None)
    if isinstance(existing, str) and existing:
        return existing
    request_id = generate_request_id()
    request.state.request_id = request_id
    return request_id
