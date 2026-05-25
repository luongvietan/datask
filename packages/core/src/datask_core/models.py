from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from datask_core.request_id import is_valid_request_id
from pydantic import BaseModel, Field, field_validator, model_validator


class ContentType(StrEnum):
    MARKDOWN = "markdown"
    TEXT = "text"


class ExtractionMode(StrEnum):
    SCHEMA = "schema"       # Layer 2: explicit JSON schema
    PROMPT = "prompt"       # Layer 3: natural language


class JobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorCode(StrEnum):
    INVALID_URL = "invalid_url"
    INVALID_API_KEY = "invalid_api_key"
    QUOTA_EXCEEDED = "quota_exceeded"
    BUDGET_EXCEEDED = "budget_exceeded"
    RATE_LIMITED = "rate_limited"
    INVALID_SCHEMA = "invalid_schema"
    FETCH_FAILED = "fetch_failed"
    EXTRACTION_FAILED = "extraction_failed"
    LAYER3_UNAVAILABLE = "layer3_unavailable"
    INTERNAL_ERROR = "internal_error"


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class FieldSchema(BaseModel):
    """Extended schema definition for a single extracted field (Layer 2)."""

    type: Literal["string", "number", "integer", "boolean"] = Field(
        ...,
        description="Expected value type for this field",
    )
    required: bool = Field(
        default=False,
        description="Whether the field must be present in extracted output",
    )
    minimum: float | None = Field(
        default=None,
        description="Minimum numeric value (number/integer fields only)",
    )
    maximum: float | None = Field(
        default=None,
        description="Maximum numeric value (number/integer fields only)",
    )
    maxLength: int | None = Field(
        default=None,
        description="Maximum string length (string fields only)",
    )
    selector: str | None = Field(
        default=None,
        description="Optional CSS selector hint for direct DOM extraction",
    )

    model_config = {"populate_by_name": True}


class ExtractRequest(BaseModel):
    url: str = Field(..., description="URL to scrape")
    schema_: dict[str, Any] | None = Field(
        default=None,
        alias="schema",
        description=(
            "JSON schema for structured extraction (Layer 2). "
            "Shorthand: {\"price\": \"number\"}. "
            "Extended field object (FieldSchema): type, required, minimum, maximum, "
            "maxLength, selector."
        ),
        json_schema_extra={
            "examples": [
                {"price": "number", "title": "string"},
                {
                    "price": {
                        "type": "number",
                        "required": True,
                        "minimum": 0,
                    },
                    "title": {
                        "type": "string",
                        "maxLength": 200,
                        "selector": "h1",
                    },
                },
            ]
        },
    )
    prompt: str | None = Field(
        default=None,
        description="Natural language description of desired data (Layer 3)",
    )
    example: dict[str, Any] | None = Field(
        default=None,
        description="Example output to guide extraction format (Layer 3 optional)",
    )

    model_config = {"populate_by_name": True}

    @field_validator("url")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @model_validator(mode="after")
    def validate_schema_or_prompt(self) -> "ExtractRequest":
        if self.schema_ is not None and self.prompt is not None:
            raise ValueError("Provide either 'schema' (Layer 2) or 'prompt' (Layer 3), not both.")
        return self

    @property
    def mode(self) -> ExtractionMode | None:
        if self.prompt is not None:
            return ExtractionMode.PROMPT
        if self.schema_ is not None:
            return ExtractionMode.SCHEMA
        return None


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ValidationError(BaseModel):
    """Single output validation error (Layer 2 post-extraction)."""

    field: str
    code: Literal["type_mismatch", "missing_required", "constraint_violation"]
    message: str


class ValidationWarning(BaseModel):
    """Non-fatal output validation warning (e.g. missing optional field)."""

    field: str
    code: Literal["missing_optional"] = "missing_optional"
    message: str


class OutputValidationResult(BaseModel):
    """Validation block attached to Layer 2 extract responses."""

    valid: bool | None = Field(
        default=None,
        description="False when output fails validation; null for Layer 3 (not validated)",
    )
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ValidationWarning] = Field(default_factory=list)


class RequestMeta(BaseModel):
    """Provenance metadata attached to every fetch/extract response."""

    request_id: str = Field(..., description="Unique trace ID, format req_{ulid}")
    layer: int | None = Field(default=None, description="API layer: 1=fetch, 2=schema, 3=prompt")
    latency_ms: int | None = Field(default=None, description="End-to-end processing time in ms")
    model: str | None = Field(default=None, description="LLM model used (Layer 3 only)")
    fetch_strategy: str | None = Field(
        default=None, description="Fetch strategy: async, stealth, or cache"
    )
    cache_hit: bool = Field(default=False, description="Whether content was served from cache")

    @field_validator("request_id")
    @classmethod
    def validate_request_id_format(cls, v: str) -> str:
        if not is_valid_request_id(v):
            raise ValueError("request_id must match req_{ulid} format")
        return v


class FetchResponse(BaseModel):
    content: str
    content_type: ContentType = ContentType.MARKDOWN
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    url: str
    meta: RequestMeta


class ExtractResponse(BaseModel):
    data: dict[str, Any]
    validation: OutputValidationResult | None = Field(
        default=None,
        description="Layer 2 output validation; omitted or valid=null for Layer 3",
    )
    inferred_schema: dict[str, Any] | None = None  # Layer 3 only
    confidence: dict[str, Any] | None = None        # Layer 2 field-level confidence
    url: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    credits_used: int = 1
    meta: RequestMeta


class ErrorResponse(BaseModel):
    error: ErrorCode
    message: str
    detail: Any | None = None
    retry_after: int | None = None       # seconds, for 429
    upgrade_url: str | None = None       # for 402


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
