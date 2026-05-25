# -*- coding: utf-8 -*-
"""Tests cho validate_output — post-LLM Layer 2 output validation."""
import pytest

from datask_core.schema_validator import validate_output


def test_valid_output_all_fields_present():
    schema = {"price": {"type": "number", "required": True}, "title": "string"}
    data = {"price": 29.99, "title": "Widget"}
    result = validate_output(data, schema)
    assert result.valid is True
    assert result.errors == []
    assert result.warnings == []


def test_missing_required_field():
    schema = {"price": {"type": "number", "required": True}}
    data = {}
    result = validate_output(data, schema)
    assert result.valid is False
    assert len(result.errors) == 1
    assert result.errors[0].field == "price"
    assert result.errors[0].code == "missing_required"


def test_required_field_null():
    schema = {"price": {"type": "number", "required": True}}
    data = {"price": None}
    result = validate_output(data, schema)
    assert result.valid is False
    assert result.errors[0].code == "missing_required"


def test_type_mismatch_string_expected_number():
    schema = {"price": "number"}
    data = {"price": "not-a-number"}
    result = validate_output(data, schema)
    assert result.valid is False
    assert any(e.code == "type_mismatch" and e.field == "price" for e in result.errors)


def test_type_mismatch_boolean():
    schema = {"in_stock": "boolean"}
    data = {"in_stock": "maybe"}
    result = validate_output(data, schema)
    assert result.valid is False
    assert result.errors[0].code == "type_mismatch"


def test_constraint_violation_minimum():
    schema = {"price": {"type": "number", "required": True, "minimum": 0}}
    data = {"price": -5}
    result = validate_output(data, schema)
    assert result.valid is False
    assert any(e.code == "constraint_violation" for e in result.errors)


def test_constraint_violation_max_length():
    schema = {"title": {"type": "string", "maxLength": 5}}
    data = {"title": "too long title"}
    result = validate_output(data, schema)
    assert result.valid is False
    assert any(e.code == "constraint_violation" for e in result.errors)


def test_missing_optional_warning():
    schema = {"price": "number", "in_stock": {"type": "boolean", "required": False}}
    data = {"price": 10}
    result = validate_output(data, schema)
    assert result.valid is True
    assert len(result.warnings) == 1
    assert result.warnings[0].field == "in_stock"
    assert result.warnings[0].code == "missing_optional"


def test_integer_type_accepts_int_rejects_float():
    schema = {"qty": "integer"}
    data = {"qty": 3.5}
    result = validate_output(data, schema)
    assert result.valid is False
    assert result.errors[0].code == "type_mismatch"


def test_valid_integer():
    schema = {"qty": {"type": "integer", "required": True}}
    data = {"qty": 42}
    result = validate_output(data, schema)
    assert result.valid is True
