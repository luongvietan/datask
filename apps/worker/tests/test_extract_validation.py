# -*- coding: utf-8 -*-
"""Unit tests — Layer 2 validation block in extract task."""
from unittest.mock import patch

from datask_core.models import ExtractionMode


def test_run_extract_layer2_includes_validation_block():
    from datask_worker.tasks.extract import run_extract

    fetch_result = {
        "content": "# Product\nPrice: $29.99",
        "fetched_at": "2026-05-25T10:00:00+00:00",
        "meta": {"fetch_strategy": "async", "cache_hit": False},
    }

    with patch("datask_worker.tasks.extract.run_fetch", return_value=fetch_result):
        with patch("datask_worker.tasks.extract._extract_with_schema") as mock_extract:
            mock_extract.return_value = (
                {"price": "not-a-number", "title": "Widget"},
                {"price": "medium", "title": "medium"},
            )
            with patch("datask_worker.usage_tracker.record_usage") as mock_usage:
                result = run_extract(
                    url="https://example.com/product",
                    mode=ExtractionMode.SCHEMA.value,
                    schema={"price": {"type": "number", "required": True}, "title": "string"},
                    prompt=None,
                    example=None,
                    api_key_id="key-1",
                    account_id="acc-1",
                    request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
                )

    assert "validation" in result
    assert result["validation"]["valid"] is False
    assert any(e["code"] == "type_mismatch" for e in result["validation"]["errors"])
    mock_usage.assert_called_once()
    assert mock_usage.call_args.kwargs["validation_valid"] is False


def test_run_extract_layer2_valid_output():
    from datask_worker.tasks.extract import run_extract

    fetch_result = {
        "content": "# Product",
        "fetched_at": "2026-05-25T10:00:00+00:00",
        "meta": {},
    }

    with patch("datask_worker.tasks.extract.run_fetch", return_value=fetch_result):
        with patch("datask_worker.tasks.extract._extract_with_schema") as mock_extract:
            mock_extract.return_value = ({"price": 29.99}, {"price": "high"})
            with patch("datask_worker.usage_tracker.record_usage") as mock_usage:
                result = run_extract(
                    url="https://example.com/product",
                    mode=ExtractionMode.SCHEMA.value,
                    schema={"price": {"type": "number", "required": True}},
                    prompt=None,
                    example=None,
                    api_key_id="key-1",
                    account_id="acc-1",
                    request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
                )

    assert result["validation"]["valid"] is True
    assert mock_usage.call_args.kwargs["validation_valid"] is True


def test_run_extract_layer3_omits_validation():
    from datask_worker.tasks.extract import run_extract

    fetch_result = {
        "content": "# Page",
        "fetched_at": "2026-05-25T10:00:00+00:00",
        "meta": {},
    }

    with patch("datask_worker.tasks.extract.run_fetch", return_value=fetch_result):
        with patch("datask_worker.tasks.extract._extract_with_llm") as mock_llm:
            mock_llm.return_value = ({"title": "Hello"}, {"title": "str"})
            with patch("datask_worker.usage_tracker.record_usage"):
                result = run_extract(
                    url="https://example.com",
                    mode=ExtractionMode.PROMPT.value,
                    schema=None,
                    prompt="Extract title",
                    example=None,
                    api_key_id="key-1",
                    account_id="acc-1",
                    request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
                )

    assert "validation" not in result
