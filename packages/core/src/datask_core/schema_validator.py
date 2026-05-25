# -*- coding: utf-8 -*-
"""Pure-Python input schema validation for Layer 2 extract requests."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from datask_core.models import OutputValidationResult, ValidationError, ValidationWarning
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


def _is_missing(value: Any) -> bool:
    return value is None


def _check_value_type(value: Any, type_name: str) -> bool:
    if type_name == "string":
        return isinstance(value, str)
    if type_name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "boolean":
        return isinstance(value, bool)
    return False


def _check_constraints(
    field_name: str,
    value: Any,
    field_def: dict[str, Any],
) -> ValidationError | None:
    type_name = field_def["type"]
    minimum = field_def.get("minimum")
    maximum = field_def.get("maximum")
    max_length = field_def.get("maxLength")

    if type_name in NUMERIC_TYPES and minimum is not None:
        if value < minimum:
            return ValidationError(
                field=field_name,
                code="constraint_violation",
                message=f"Value {value} is below minimum {minimum}",
            )

    if type_name in NUMERIC_TYPES and maximum is not None:
        if value > maximum:
            return ValidationError(
                field=field_name,
                code="constraint_violation",
                message=f"Value {value} is above maximum {maximum}",
            )

    if type_name == "string" and max_length is not None:
        if len(value) > max_length:
            return ValidationError(
                field=field_name,
                code="constraint_violation",
                message=f"String length {len(value)} exceeds maxLength {max_length}",
            )

    return None


def validate_output(data: dict[str, Any], schema: dict[str, Any]) -> OutputValidationResult:
    """Validate Layer 2 extracted data against schema. No I/O."""
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    normalized = normalize_input_schema(schema)

    for field_name, field_def in normalized.items():
        required = bool(field_def.get("required", False))
        type_name = field_def["type"]
        value = data.get(field_name)

        if _is_missing(value):
            if required:
                errors.append(
                    ValidationError(
                        field=field_name,
                        code="missing_required",
                        message=f"Required field '{field_name}' is missing or null",
                    )
                )
            else:
                warnings.append(
                    ValidationWarning(
                        field=field_name,
                        code="missing_optional",
                        message=f"Optional field '{field_name}' is missing or null",
                    )
                )
            continue

        if not _check_value_type(value, type_name):
            errors.append(
                ValidationError(
                    field=field_name,
                    code="type_mismatch",
                    message=(
                        f"Field '{field_name}' expected type '{type_name}', "
                        f"got {type(value).__name__}"
                    ),
                )
            )
            continue

        constraint_err = _check_constraints(field_name, value, field_def)
        if constraint_err is not None:
            errors.append(constraint_err)

    return OutputValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
