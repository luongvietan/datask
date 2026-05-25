# -*- coding: utf-8 -*-
"""Tests cho run_extract meta output."""
from unittest.mock import patch

from datask_core.models import ExtractionMode


def test_run_extract_includes_meta_and_propagates_request_id():
    request_id = "req_01JABCDEFGHJKMNPQRSTVWXYZ0"
    fetch_result = {
        "content": "# Product",
        "fetched_at": "2026-01-01T00:00:00+00:00",
        "meta": {
            "request_id": request_id,
            "fetch_strategy": "cache",
            "cache_hit": True,
        },
    }

    with patch("datask_worker.tasks.extract.run_fetch", return_value=fetch_result) as mock_fetch:
        with patch(
            "datask_worker.tasks.extract._extract_with_schema",
            return_value=({"title": "Widget"}, {"title": "high"}),
        ):
            with patch("datask_worker.usage_tracker.record_usage"):
                with patch("datask_worker.tasks.extract._check_quota_alert"):
                    from datask_worker.tasks.extract import run_extract

                    result = run_extract(
                        url="https://example.com",
                        mode=ExtractionMode.SCHEMA.value,
                        schema={"title": "string"},
                        prompt=None,
                        example=None,
                        api_key_id="key-1",
                        account_id="acc-1",
                        request_id=request_id,
                    )

    mock_fetch.assert_called_once_with("https://example.com", request_id=request_id)
    assert result["meta"]["request_id"] == request_id
    assert result["meta"]["layer"] == 2
    assert result["meta"]["fetch_strategy"] == "cache"
    assert result["meta"]["cache_hit"] is True
