# -*- coding: utf-8 -*-
"""
Tests cho billing logic: success-only billing.
Failed jobs → credits_used=0
Validation fail → credits_used=0 (khi có validation)
Success → credits_used theo layer
"""
from unittest.mock import MagicMock, patch

import pytest
from datask_core.models import ExtractionMode


def test_compute_credits_success_layer2():
    """Successful L2 extraction → 1 credit"""
    from datask_worker.usage_tracker import compute_credits

    credits = compute_credits(
        success=True,
        validation_valid=True,
        layer=2,
    )
    assert credits == 1


def test_compute_credits_success_layer3():
    """Successful L3 extraction → 2 credits"""
    from datask_worker.usage_tracker import compute_credits

    credits = compute_credits(
        success=True,
        validation_valid=None,  # L3 không có validation
        layer=3,
    )
    assert credits == 2


def test_compute_credits_failed_job():
    """Failed job (success=False) → 0 credits regardless of layer"""
    from datask_worker.usage_tracker import compute_credits

    credits = compute_credits(
        success=False,
        validation_valid=None,
        layer=2,
    )
    assert credits == 0

    credits = compute_credits(
        success=False,
        validation_valid=None,
        layer=3,
    )
    assert credits == 0


def test_compute_credits_validation_fail():
    """Validation fail (validation_valid=False) → 0 credits"""
    from datask_worker.usage_tracker import compute_credits

    credits = compute_credits(
        success=True,
        validation_valid=False,
        layer=2,
    )
    assert credits == 0


def test_compute_credits_layer1_success():
    """Successful L1 fetch → 1 credit"""
    from datask_worker.usage_tracker import compute_credits

    credits = compute_credits(
        success=True,
        validation_valid=None,
        layer=1,
    )
    assert credits == 1


def test_compute_credits_layer1_failed():
    """Failed L1 fetch → 0 credits"""
    from datask_worker.usage_tracker import compute_credits

    credits = compute_credits(
        success=False,
        validation_valid=None,
        layer=1,
    )
    assert credits == 0


def test_run_extract_failed_job_zero_credits():
    """Extract job that fails → credits_used=0 in usage record"""
    from datask_worker.tasks.extract import run_extract

    with patch("datask_worker.tasks.extract.run_fetch") as mock_fetch:
        mock_fetch.side_effect = RuntimeError("Fetch failed")
        with patch("datask_worker.usage_tracker.record_usage") as mock_usage:
            with pytest.raises(RuntimeError):
                run_extract(
                    url="https://example.com",
                    mode=ExtractionMode.SCHEMA.value,
                    schema={"price": "number"},
                    prompt=None,
                    example=None,
                    api_key_id="key-1",
                    account_id="acc-1",
                    request_id="req_01JABCDEFGHJKMNPQRSTVWXYZ0",
                )

            mock_usage.assert_called_once()
            assert mock_usage.call_args.kwargs["credits_used"] == 0
            assert mock_usage.call_args.kwargs["success"] is False


def test_run_extract_validation_fail_zero_credits():
    """Extract job with validation fail → credits_used=0"""
    from datask_worker.tasks.extract import run_extract

    fetch_result = {
        "content": "# Product\nPrice: not-a-number",
        "fetched_at": "2026-05-25T10:00:00+00:00",
        "meta": {"fetch_strategy": "async", "cache_hit": False},
    }

    with patch("datask_worker.tasks.extract.run_fetch", return_value=fetch_result):
        with patch("datask_worker.tasks.extract._extract_with_schema") as mock_extract:
            mock_extract.return_value = (
                {"price": "not-a-number"},
                {"price": "medium"},
            )
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

                mock_usage.assert_called_once()
                assert mock_usage.call_args.kwargs["credits_used"] == 0
                assert mock_usage.call_args.kwargs["success"] is True
                assert mock_usage.call_args.kwargs["validation_valid"] is False
                assert result["credits_used"] == 0


def test_run_extract_success_layer2_one_credit():
    """Successful L2 extraction with valid output → credits_used=1"""
    from datask_worker.tasks.extract import run_extract

    fetch_result = {
        "content": "# Product\nPrice: $29.99",
        "fetched_at": "2026-05-25T10:00:00+00:00",
        "meta": {"fetch_strategy": "async", "cache_hit": False},
    }

    with patch("datask_worker.tasks.extract.run_fetch", return_value=fetch_result):
        with patch("datask_worker.tasks.extract._extract_with_schema") as mock_extract:
            mock_extract.return_value = (
                {"price": 29.99},
                {"price": "high"},
            )
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

                mock_usage.assert_called_once()
                assert mock_usage.call_args.kwargs["credits_used"] == 1
                assert mock_usage.call_args.kwargs["success"] is True
                assert mock_usage.call_args.kwargs["validation_valid"] is True
                assert result["credits_used"] == 1


def test_run_extract_success_layer3_two_credits():
    """Successful L3 extraction → credits_used=2"""
    from datask_worker.tasks.extract import run_extract

    fetch_result = {
        "content": "# Page",
        "fetched_at": "2026-05-25T10:00:00+00:00",
        "meta": {},
    }

    with patch("datask_worker.tasks.extract.run_fetch", return_value=fetch_result):
        with patch("datask_worker.tasks.extract._extract_with_llm") as mock_llm:
            mock_llm.return_value = ({"title": "Hello"}, {"title": "str"})
            with patch("datask_worker.usage_tracker.record_usage") as mock_usage:
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

                mock_usage.assert_called_once()
                assert mock_usage.call_args.kwargs["credits_used"] == 2
                assert mock_usage.call_args.kwargs["success"] is True
                assert result["credits_used"] == 2
