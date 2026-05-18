from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


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
    RATE_LIMITED = "rate_limited"
    INVALID_SCHEMA = "invalid_schema"
    FETCH_FAILED = "fetch_failed"
    EXTRACTION_FAILED = "extraction_failed"
    LAYER3_UNAVAILABLE = "layer3_unavailable"
    INTERNAL_ERROR = "internal_error"


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class ExtractRequest(BaseModel):
    url: str = Field(..., description="URL to scrape")
    schema_: dict[str, Any] | None = Field(
        default=None,
        alias="schema",
        description="JSON schema for structured extraction (Layer 2)",
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


class FetchResponse(BaseModel):
    content: str
    content_type: ContentType = ContentType.MARKDOWN
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    url: str


class ExtractResponse(BaseModel):
    data: dict[str, Any]
    inferred_schema: dict[str, Any] | None = None  # Layer 3 only
    confidence: dict[str, Any] | None = None        # Layer 2 field-level confidence
    url: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    credits_used: int = 1


class ErrorResponse(BaseModel):
    error: ErrorCode
    message: str
    detail: str | None = None
    retry_after: int | None = None       # seconds, for 429
    upgrade_url: str | None = None       # for 402


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
