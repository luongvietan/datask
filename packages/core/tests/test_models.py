# -*- coding: utf-8 -*-
"""Tests cho Pydantic models."""
import pytest
from datask_core.models import ExtractRequest, ExtractionMode


def test_extract_request_schema_mode():
    req = ExtractRequest(
        url="https://example.com",
        schema_={"price": "number"},
    )
    assert req.mode == ExtractionMode.SCHEMA
    assert req.schema_ == {"price": "number"}


def test_extract_request_prompt_mode():
    req = ExtractRequest(
        url="https://example.com",
        prompt="Extract the product name and price",
    )
    assert req.mode == ExtractionMode.PROMPT
    assert req.prompt == "Extract the product name and price"


def test_extract_request_both_fails():
    """Không được có cả schema và prompt."""
    with pytest.raises(ValueError):
        ExtractRequest(
            url="https://example.com",
            schema_={"name": "string"},
            prompt="Extract name",
        )


def test_extract_request_invalid_url():
    with pytest.raises(ValueError):
        ExtractRequest(url="not-a-url")
