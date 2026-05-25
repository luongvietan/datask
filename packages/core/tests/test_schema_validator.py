# -*- coding: utf-8 -*-
"""Tests cho validate_input_schema — pre-enqueue schema validation."""
import pytest

from datask_core.schema_validator import validate_input_schema


def test_valid_shorthand_number():
    result = validate_input_schema({"price": "number"})
    assert result.valid is True
    assert result.errors == []


def test_valid_shorthand_string():
    result = validate_input_schema({"title": "string"})
    assert result.valid is True


def test_valid_extended_format_all_fields():
    result = validate_input_schema(
        {
            "price": {
                "type": "number",
                "required": True,
                "minimum": 0,
                "maximum": 9999,
            },
            "title": {
                "type": "string",
                "required": False,
                "maxLength": 200,
                "selector": ".product-title",
            },
        }
    )
    assert result.valid is True


def test_unknown_type_rejected():
    result = validate_input_schema({"price": "currency"})
    assert result.valid is False
    assert any("price" in e.field for e in result.errors)


def test_conflicting_min_max_rejected():
    result = validate_input_schema(
        {"price": {"type": "number", "minimum": 100, "maximum": 10}}
    )
    assert result.valid is False
    assert any("minimum" in e.message.lower() or "maximum" in e.message.lower() for e in result.errors)


def test_max_length_on_number_rejected():
    result = validate_input_schema({"price": {"type": "number", "maxLength": 10}})
    assert result.valid is False


def test_minimum_on_string_rejected():
    result = validate_input_schema({"title": {"type": "string", "minimum": 1}})
    assert result.valid is False


def test_empty_schema_rejected():
    result = validate_input_schema({})
    assert result.valid is False


def test_required_boolean_field_valid():
    result = validate_input_schema({"in_stock": {"type": "boolean", "required": True}})
    assert result.valid is True


def test_integer_with_min_max_valid():
    result = validate_input_schema({"quantity": {"type": "integer", "minimum": 1, "maximum": 100}})
    assert result.valid is True


def test_invalid_field_value_type_rejected():
    result = validate_input_schema({"price": ["number"]})
    assert result.valid is False


def test_extended_format_missing_type_rejected():
    result = validate_input_schema({"price": {"required": True}})
    assert result.valid is False


def test_unknown_extended_property_rejected():
    result = validate_input_schema({"price": {"type": "number", "pattern": "^[0-9]+$"}})
    assert result.valid is False


def test_max_length_zero_rejected():
    result = validate_input_schema({"title": {"type": "string", "maxLength": 0}})
    assert result.valid is False


def test_max_length_negative_rejected():
    result = validate_input_schema({"title": {"type": "string", "maxLength": -1}})
    assert result.valid is False
