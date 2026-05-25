# -*- coding: utf-8 -*-
"""Tests cho fetch meta output."""
from unittest.mock import patch


def test_build_meta_shape():
    from datask_worker.tasks.fetch import _build_meta

    meta = _build_meta(
        request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
        layer=1,
        latency_ms=500,
        fetch_strategy="async",
        cache_hit=False,
    )
    assert meta["request_id"].startswith("req_")
    assert meta["layer"] == 1
    assert meta["latency_ms"] == 500
    assert meta["fetch_strategy"] == "async"
    assert meta["cache_hit"] is False


def test_run_fetch_cache_hit_includes_meta():
    from datask_worker.tasks.fetch import run_fetch

    request_id = "req_01JABCDEFGHJKMNPQRSTVWXYZ0"
    with patch("datask_worker.tasks.fetch._try_get_cache", return_value="# Cached"):
        result = run_fetch(
            "https://example.com",
            account_id=None,
            request_id=request_id,
        )

    assert result["meta"]["request_id"] == request_id
    assert result["meta"]["layer"] == 1
    assert result["meta"]["cache_hit"] is True
    assert result["meta"]["fetch_strategy"] == "cache"
