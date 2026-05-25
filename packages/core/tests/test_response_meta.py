# -*- coding: utf-8 -*-
"""Tests cho RequestMeta và response models."""
import pytest

from datask_core.models import ExtractResponse, FetchResponse, RequestMeta


def test_request_meta_minimal():
    meta = RequestMeta(request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0")
    assert meta.request_id.startswith("req_")
    assert meta.layer is None
    assert meta.cache_hit is False


def test_request_meta_rejects_invalid_request_id():
    with pytest.raises(ValueError):
        RequestMeta(request_id="req_invalid")


def test_fetch_response_with_meta():
    meta = RequestMeta(request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0", layer=1, latency_ms=120)
    resp = FetchResponse(
        content="# Hello",
        url="https://example.com",
        meta=meta,
    )
    assert resp.meta is not None
    assert resp.meta.request_id.startswith("req_")
    assert resp.meta.layer == 1


def test_extract_response_with_meta():
    meta = RequestMeta(
        request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
        layer=2,
        latency_ms=1840,
    )
    resp = ExtractResponse(
        data={"title": "Widget"},
        url="https://example.com",
        meta=meta,
    )
    assert resp.meta is not None
    assert resp.meta.layer == 2
