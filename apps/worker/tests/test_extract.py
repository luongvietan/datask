# -*- coding: utf-8 -*-
"""Unit tests cho extract task."""
from unittest.mock import MagicMock, patch
import json
import pytest


def test_coerce_value_number():
    from datask_worker.tasks.extract import _coerce_value
    assert _coerce_value("$1,299.99", "number") == 1299.99
    assert _coerce_value("42", "integer") == 42
    assert _coerce_value("yes", "boolean") is True


def test_coerce_value_none():
    from datask_worker.tasks.extract import _coerce_value
    assert _coerce_value(None, "string") is None
    assert _coerce_value(None, "number") is None


def test_extract_with_schema_llm_fallback():
    """Schema without selectors should trigger LLM-light fallback."""
    from datask_worker.tasks.extract import _extract_with_schema

    fake_llm_response = {"title": "Test Page", "price": "99.99"}

    with patch("datask_worker.tasks.extract._extract_with_llm") as mock_llm:
        mock_llm.return_value = (fake_llm_response, {})
        result, confidence = _extract_with_schema(
            content="Test Page costs $99.99",
            html="",
            schema={"title": "string", "price": "number"},
        )

    assert result["title"] == "Test Page"
    assert confidence["title"] == "medium"


def test_build_extraction_prompt_contains_content():
    from datask_worker.tasks.extract import _build_extraction_prompt
    prompt = _build_extraction_prompt(
        content="This is the page content",
        user_prompt="Extract the title",
        example=None,
    )
    assert "This is the page content" in prompt
    assert "Extract the title" in prompt
