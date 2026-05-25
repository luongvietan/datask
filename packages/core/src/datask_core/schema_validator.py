# -*- coding: utf-8 -*-
"""Pure-Python input schema validation for Layer 2 extract requests."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

SUPPORTED_TYPES = frozenset({"string", "number", "integer", "boolean"})
NUMERIC_TYPES = frozenset({"number", "integer"})
ALLOWED_FIELD_KEYS = frozenset(
    {"type", "required", "minimum", "maximum", "maxLength", "selector"}
)


@dataclass
class SchemaValidationError:
    field: str
    message: str


@dataclass
class ValidationResult:
    valid: bool
    errors: list[SchemaValidationError] = field(default_factory=list)


def _add_error(errors: list[SchemaValidationError], field_name: str, message: str) -> None:
    errors.append(SchemaValidationError(field=field_name, message=message))


def _validate_field_definition(
    field_name: str,
    definition: Any,
    errors: list[SchemaValidationError],
) -> str | None:
    """Validate one field definition. Returns resolved type or None if invalid."""
    if isinstance(definition, str):
        type_name = definition
        required = False
        minimum = maximum = max_length = None
        selector = None
    elif isinstance(definition, dict):
        unknown_keys = set(definition.keys()) - ALLOWED_FIELD_KEYS
        if unknown_keys:
            _add_error(
                errors,
                field_name,
                f"Unknown schema properties: {', '.join(sorted(unknown_keys))}",
            )
            return None

        raw_type = definition.get("type")
        if not isinstance(raw_type, str):
            _add_error(errors, field_name, "Extended schema fields must include a string 'type'")
            return None
        type_name = raw_type
        required = definition.get("required", False)
        minimum = definition.get("minimum")
        maximum = definition.get("maximum")
        max_length = definition.get("maxLength")
        selector = definition.get("selector")

        if not isinstance(required, bool):
            _add_error(errors, field_name, "'required' must be a boolean")
            return None
        if minimum is not None and not isinstance(minimum, (int, float)):
            _add_error(errors, field_name, "'minimum' must be a number")
            return None
        if maximum is not None and not isinstance(maximum, (int, float)):
            _add_error(errors, field_name, "'maximum' must be a number")
            return None
        if max_length is not None and not isinstance(max_length, int):
            _add_error(errors, field_name, "'maxLength' must be an integer")
            return None
        if max_length is not None and max_length <= 0:
            _add_error(errors, field_name, "'maxLength' must be greater than 0")
            return None
        if selector is not None and not isinstance(selector, str):
            _add_error(errors, field_name, "'selector' must be a string")
            return None
    else:
        _add_error(
            errors,
            field_name,
            "Schema field must be a type string or an extended object",
        )
        return None

    if type_name not in SUPPORTED_TYPES:
        _add_error(
            errors,
            field_name,
            f"Unsupported type '{type_name}'. Supported: string, number, integer, boolean",
        )
        return None

    if max_length is not None and type_name != "string":
        _add_error(errors, field_name, "'maxLength' is only valid for string fields")

    if minimum is not None and type_name not in NUMERIC_TYPES:
        _add_error(errors, field_name, "'minimum' is only valid for number or integer fields")

    if maximum is not None and type_name not in NUMERIC_TYPES:
        _add_error(errors, field_name, "'maximum' is only valid for number or integer fields")

    if (
        minimum is not None
        and maximum is not None
        and minimum > maximum
    ):
        _add_error(errors, field_name, "'minimum' cannot be greater than 'maximum'")

    return type_name


def validate_input_schema(schema: dict[str, Any]) -> ValidationResult:
    """Validate Layer 2 input schema before enqueue. No I/O."""
    errors: list[SchemaValidationError] = []

    if not schema:
        _add_error(errors, "_schema", "Schema must include at least one field")
        return ValidationResult(valid=False, errors=errors)

    if not isinstance(schema, dict):
        _add_error(errors, "_schema", "Schema must be a JSON object")
        return ValidationResult(valid=False, errors=errors)

    for field_name, definition in schema.items():
        if not isinstance(field_name, str) or not field_name.strip():
            _add_error(errors, str(field_name), "Field name must be a non-empty string")
            continue
        _validate_field_definition(field_name, definition, errors)

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def normalize_field_schema(definition: str | dict[str, Any]) -> dict[str, Any]:
    """Normalize shorthand or extended field definition to canonical extended format."""
    if isinstance(definition, BaseModel):
        definition = definition.model_dump(exclude_none=True)

    if isinstance(definition, str):
        return {"type": definition, "required": False}

    normalized: dict[str, Any] = {
        "type": definition["type"],
        "required": bool(definition.get("required", False)),
    }
    for key in ("minimum", "maximum", "maxLength", "selector"):
        if key in definition and definition[key] is not None:
            normalized[key] = definition[key]
    return normalized


def normalize_input_schema(schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Normalize all fields in a schema dict to extended format."""
    return {field: normalize_field_schema(defn) for field, defn in schema.items()}
