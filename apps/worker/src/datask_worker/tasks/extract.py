# -*- coding: utf-8 -*-
"""
Layer 2/3 extract task — runs inside RQ worker.
Layer 2: schema-driven extraction (CSS selector hint or LLM-light fallback).
Layer 3: LLM (GPT-4o-mini) schema inference from prompt + content.
"""
from __future__ import annotations

import json
import os
import time
from datetime import UTC, datetime
from typing import Any

import structlog
from datask_core.config import get_settings
from datask_core.models import ExtractionMode

from datask_worker.tasks.fetch import run_fetch

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Layer 2 — schema-driven extraction
# ---------------------------------------------------------------------------


def _coerce_value(value: Any, type_hint: str) -> Any:
    """Coerce value to the declared type hint where possible."""
    if value is None:
        return None
    try:
        if type_hint in ("number", "float"):
            cleaned = str(value).replace("$", "").replace(",", "").strip()
            return float(cleaned)
        if type_hint in ("integer", "int"):
            cleaned = str(value).replace(",", "").strip()
            return int(float(cleaned))
        if type_hint == "boolean":
            return str(value).lower() in ("true", "yes", "1", "in stock", "available")
        return str(value).strip()
    except (ValueError, TypeError):
        return value


def _extract_with_schema(
    content: str,
    html: str,
    schema: dict[str, Any],
    page=None,  # Scrapling page object if available
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Extract data according to schema.
    - Fields with 'selector' key → use Scrapling CSS selector on page object.
    - Remaining fields → LLM-light extraction.
    Returns (data, confidence_map).
    """
    result: dict[str, Any] = {}
    confidence: dict[str, Any] = {}

    selector_fields = {}
    plain_fields = {}

    for field, hint in schema.items():
        if isinstance(hint, dict) and "selector" in hint:
            selector_fields[field] = hint
        else:
            plain_fields[field] = hint

    if selector_fields and page is not None:
        for field, hint in selector_fields.items():
            selector = hint.get("selector", "")
            type_hint = hint.get("type", "string")
            try:
                el = page.css_first(selector)
                raw_val = el.text(strip=True) if el else None
                result[field] = _coerce_value(raw_val, type_hint)
                confidence[field] = "high" if raw_val else None
            except Exception:
                result[field] = None
                confidence[field] = None
    elif selector_fields:
        # No page object — fall back to treating selector fields as plain
        for field in selector_fields:
            plain_fields[field] = selector_fields[field].get("type", "string")

    if plain_fields:
        try:
            llm_result, _ = _extract_with_llm(
                content=content,
                prompt=f"Extract these fields from the page: {list(plain_fields.keys())}. Return JSON with exactly these keys.",
                example=None,
                schema_hint=plain_fields,
            )
            for field in plain_fields:
                if field in llm_result:
                    type_hint = plain_fields[field] if isinstance(plain_fields[field], str) else "string"
                    result[field] = _coerce_value(llm_result[field], type_hint)
                    confidence[field] = "medium"
                else:
                    result[field] = None
                    confidence[field] = None
        except Exception as e:
            logger.warning("llm_extraction_failed", error=str(e))
            for field in plain_fields:
                if field not in result:
                    result[field] = None
                    confidence[field] = None

    return result, confidence


# ---------------------------------------------------------------------------
# Layer 3 — natural language extraction via LLM
# ---------------------------------------------------------------------------


def _build_extraction_prompt(
    content: str,
    user_prompt: str,
    example: dict | None,
    schema_hint: dict | None = None,
) -> str:
    example_section = ""
    if example:
        example_section = f"\n\nExample output format:\n```json\n{json.dumps(example, indent=2)}\n```"

    schema_section = ""
    if schema_hint:
        schema_section = f"\n\nRequired output schema: {json.dumps(schema_hint)}"

    truncated = content[:12000] if len(content) > 12000 else content

    return f"""You are a data extraction assistant. Extract structured data from the web page content below.

User request: {user_prompt}{schema_section}{example_section}

Web page content (Markdown):
---
{truncated}
---

Respond with ONLY a valid JSON object. No explanation, no markdown fences. The JSON must match what the user requested."""


def _extract_with_llm(
    content: str,
    prompt: str,
    example: dict[str, Any] | None,
    schema_hint: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Returns (extracted_data, inferred_schema).
    Raises RuntimeError if LLM is not available.
    """
    from openai import OpenAI

    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not configured — Layer 3 unavailable")

    client = OpenAI(api_key=settings.openai_api_key)

    messages = [
        {
            "role": "system",
            "content": "You extract structured data from web pages. Always respond with valid JSON only.",
        },
        {
            "role": "user",
            "content": _build_extraction_prompt(content, prompt, example, schema_hint),
        },
    ]

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0,
        max_tokens=2048,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"
    extracted: dict[str, Any] = json.loads(raw)

    inferred_schema = {k: type(v).__name__ for k, v in extracted.items()}
    return extracted, inferred_schema


# ---------------------------------------------------------------------------
# RQ task entry point
# ---------------------------------------------------------------------------


def run_extract(
    url: str,
    mode: str,
    schema: dict[str, Any] | None,
    prompt: str | None,
    example: dict[str, Any] | None,
    api_key_id: str,
    account_id: str,
) -> dict:
    log = logger.bind(url=url, mode=mode, api_key_id=api_key_id)
    log.info("extract_start")
    start_ms = int(time.time() * 1000)

    success = False
    error_code = None
    data: dict[str, Any] = {}
    inferred_schema: dict[str, Any] | None = None
    confidence: dict[str, Any] | None = None
    layer = 2 if mode == ExtractionMode.SCHEMA else 3
    credits_used = 1 if mode == ExtractionMode.SCHEMA else 2

    try:
        fetch_result = run_fetch(url)
        content: str = fetch_result["content"]

        if mode == ExtractionMode.SCHEMA:
            if not schema:
                raise ValueError("schema required for Layer 2 extraction")
            data, confidence = _extract_with_schema(content=content, html="", schema=schema)

        elif mode == ExtractionMode.PROMPT:
            if not prompt:
                raise ValueError("prompt required for Layer 3 extraction")
            data, inferred_schema = _extract_with_llm(content, prompt, example)

        else:
            raise ValueError(f"Unknown extraction mode: {mode}")

        success = True
        log.info("extract_complete", fields=list(data.keys()))

    except Exception as e:
        error_code = "extraction_failed"
        log.error("extract_error", error=str(e))
        raise
    finally:
        response_time_ms = int(time.time() * 1000) - start_ms
        try:
            from datask_worker.usage_tracker import record_usage
            record_usage(
                account_id=account_id,
                api_key_id=api_key_id,
                url=url,
                layer=layer,
                success=success,
                credits_used=credits_used,
                response_time_ms=response_time_ms,
                error_code=error_code,
            )
        except Exception:
            pass

        _check_quota_alert(account_id=account_id)

    result: dict[str, Any] = {
        "data": data,
        "inferred_schema": inferred_schema,
        "url": url,
        "fetched_at": fetch_result["fetched_at"],
        "credits_used": credits_used,
    }
    if confidence:
        result["confidence"] = confidence

    return result


def _check_quota_alert(account_id: str) -> None:
    """Send email alert when quota reaches 80% or 100%. Uses raw SQL to avoid cross-package import."""
    try:
        from sqlalchemy import text

        from datask_worker.db import get_session

        with get_session() as session:
            row = session.execute(
                text("SELECT tier, email FROM accounts WHERE id = :id"),
                {"id": account_id},
            ).fetchone()

            if not row or row.tier != "free":
                return

            now = datetime.now(UTC)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            count = session.execute(
                text(
                    "SELECT COUNT(*) FROM usage_records "
                    "WHERE account_id = :id AND success = true AND created_at >= :month_start"
                ),
                {"id": account_id, "month_start": month_start},
            ).scalar() or 0

        quota = int(os.environ.get("FREE_TIER_MONTHLY_QUOTA", "500"))
        pct = int(count / quota * 100) if quota > 0 else 0

        alert_key = None
        if pct >= 100:
            alert_key = f"quota:alert:100:{account_id}:{now.strftime('%Y-%m')}"
        elif pct >= 80:
            alert_key = f"quota:alert:80:{account_id}:{now.strftime('%Y-%m')}"

        if alert_key:
            import redis as sync_redis

            r = sync_redis.from_url(
                os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
                decode_responses=True,
            )
            if not r.exists(alert_key):
                r.setex(alert_key, 60 * 60 * 24 * 32, "sent")
                logger.info(
                    "quota_alert_triggered",
                    account_id=account_id,
                    email=row.email,
                    pct=pct,
                )
    except Exception as e:
        logger.warning("quota_alert_check_failed", error=str(e))
