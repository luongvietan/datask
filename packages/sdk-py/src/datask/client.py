# -*- coding: utf-8 -*-
"""
Datask Python SDK — v0.1
Cả sync và async client.

Usage:
  # Sync
  import datask
  client = datask.Client(api_key="dtsk_live_...")
  content = client.fetch("https://example.com")
  data = client.extract("https://shop.com/product", schema={"price": "number"})

  # Async
  async with datask.AsyncClient(api_key="...") as client:
      content = await client.fetch("https://example.com")
"""
from __future__ import annotations

import os
import time
from typing import Any, TypedDict

import httpx

DEFAULT_BASE_URL = "https://api.datask.run"
DEFAULT_TIMEOUT = 90.0
MAX_POLL_SECONDS = 120
POLL_INTERVAL = 2.0


class DataskError(Exception):
    """Base error."""


class AuthenticationError(DataskError):
    """401 — Invalid or missing API key."""


class QuotaExceededError(DataskError):
    """402 — Monthly quota exceeded. Upgrade to continue."""

    def __init__(self, message: str, upgrade_url: str | None = None) -> None:
        super().__init__(message)
        self.upgrade_url = upgrade_url


class RateLimitError(DataskError):
    """429 — Rate limit hit."""

    def __init__(self, message: str, retry_after: int = 60) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class FetchError(DataskError):
    """Failed to fetch URL."""


class ValidationErrorItem(TypedDict):
    field: str
    code: str
    message: str


class ValidationWarningItem(TypedDict):
    field: str
    code: str
    message: str


class ValidationBlock(TypedDict, total=False):
    valid: bool | None
    errors: list[ValidationErrorItem]
    warnings: list[ValidationWarningItem]


class ExtractResult(TypedDict, total=False):
    data: dict[str, Any]
    validation: ValidationBlock
    confidence: dict[str, Any]
    inferred_schema: dict[str, Any]
    meta: dict[str, Any]
    url: str
    fetched_at: str
    credits_used: int


def _want_full_response(
    *,
    schema: dict[str, Any] | None,
    full_response: bool | None,
) -> bool:
    """Layer 2 (schema) returns full payload by default so validation is visible."""
    if full_response is not None:
        return full_response
    return schema is not None


# ---------------------------------------------------------------------------
# Sync Client
# ---------------------------------------------------------------------------


class Client:
    """Synchronous Datask client."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._api_key = api_key or os.environ.get("DATASK_API_KEY", "")
        if not self._api_key:
            raise AuthenticationError(
                "API key required. Set DATASK_API_KEY env var or pass api_key=..."
            )
        self._base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=timeout,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.is_success:
            return
        try:
            body = resp.json()
        except Exception:
            body = {}

        msg = body.get("message", f"HTTP {resp.status_code}")
        code = body.get("error", "unknown_error")

        if resp.status_code == 401:
            raise AuthenticationError(msg)
        if resp.status_code == 402:
            raise QuotaExceededError(msg, body.get("upgrade_url"))
        if resp.status_code == 429:
            raise RateLimitError(msg, body.get("retry_after", 60))
        raise DataskError(f"[{code}] {msg}")

    def fetch(self, url: str) -> str:
        """
        Layer 1 — fetch clean Markdown from any URL.
        Returns Markdown string.
        """
        resp = self._http.get("/v1/fetch", params={"url": url})
        self._raise_for_status(resp)
        return resp.json()["content"]

    def extract(
        self,
        url: str,
        schema: dict[str, Any] | None = None,
        prompt: str | None = None,
        example: dict[str, Any] | None = None,
        async_mode: bool = False,
        *,
        full_response: bool | None = None,
    ) -> dict[str, Any]:
        """
        Layer 2 (schema) or Layer 3 (prompt) extraction.

        Layer 2 returns the full API payload by default (includes validation block).
        Layer 3 returns extracted data only unless full_response=True.
        Pass full_response=False on Layer 2 to get just the data dict.

        async_mode=True: sends X-Datask-Async: true header, polls until done.
        """
        body: dict[str, Any] = {"url": url}
        if schema:
            body["schema"] = schema
        elif prompt:
            body["prompt"] = prompt
            if example:
                body["example"] = example
        else:
            raise ValueError("Provide either schema (Layer 2) or prompt (Layer 3)")

        want_full = _want_full_response(schema=schema, full_response=full_response)
        headers = {"X-Datask-Async": "true"} if async_mode else {}

        resp = self._http.post("/v1/extract", json=body, headers=headers)
        self._raise_for_status(resp)
        data = resp.json()

        if resp.status_code == 202:
            # Poll until complete
            job_id = data["job_id"]
            polled = self._poll_job(job_id, full_response=want_full)
            return polled

        if want_full:
            return data
        return data.get("data", data)

    def _poll_job(self, job_id: str, *, full_response: bool = False) -> dict[str, Any]:
        deadline = time.time() + MAX_POLL_SECONDS
        while time.time() < deadline:
            resp = self._http.get(f"/v1/jobs/{job_id}")
            self._raise_for_status(resp)
            job = resp.json()
            if job["status"] == "completed":
                result = job.get("result", {})
                if full_response:
                    return result if isinstance(result, dict) else {}
                return result.get("data", result) if isinstance(result, dict) else {}
            if job["status"] == "failed":
                raise FetchError(f"Job {job_id} failed")
            time.sleep(POLL_INTERVAL)
        raise TimeoutError(f"Job {job_id} timed out after {MAX_POLL_SECONDS}s")


# ---------------------------------------------------------------------------
# Async Client
# ---------------------------------------------------------------------------


class AsyncClient:
    """Asynchronous Datask client."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._api_key = api_key or os.environ.get("DATASK_API_KEY", "")
        if not self._api_key:
            raise AuthenticationError(
                "API key required. Set DATASK_API_KEY env var or pass api_key=..."
            )
        self._base_url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.is_success:
            return
        try:
            body = resp.json()
        except Exception:
            body = {}

        msg = body.get("message", f"HTTP {resp.status_code}")
        code = body.get("error", "unknown_error")

        if resp.status_code == 401:
            raise AuthenticationError(msg)
        if resp.status_code == 402:
            raise QuotaExceededError(msg, body.get("upgrade_url"))
        if resp.status_code == 429:
            raise RateLimitError(msg, body.get("retry_after", 60))
        raise DataskError(f"[{code}] {msg}")

    async def fetch(self, url: str) -> str:
        resp = await self._http.get("/v1/fetch", params={"url": url})
        self._raise_for_status(resp)
        return resp.json()["content"]

    async def extract(
        self,
        url: str,
        schema: dict[str, Any] | None = None,
        prompt: str | None = None,
        example: dict[str, Any] | None = None,
        async_mode: bool = False,
        *,
        full_response: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"url": url}
        if schema:
            body["schema"] = schema
        elif prompt:
            body["prompt"] = prompt
            if example:
                body["example"] = example
        else:
            raise ValueError("Provide either schema (Layer 2) or prompt (Layer 3)")

        want_full = _want_full_response(schema=schema, full_response=full_response)
        headers = {"X-Datask-Async": "true"} if async_mode else {}

        resp = await self._http.post("/v1/extract", json=body, headers=headers)
        self._raise_for_status(resp)
        data = resp.json()

        if resp.status_code == 202:
            job_id = data["job_id"]
            return await self._poll_job(job_id, full_response=want_full)

        if want_full:
            return data
        return data.get("data", data)

    async def _poll_job(self, job_id: str, *, full_response: bool = False) -> dict[str, Any]:
        import asyncio

        deadline = time.time() + MAX_POLL_SECONDS
        while time.time() < deadline:
            resp = await self._http.get(f"/v1/jobs/{job_id}")
            self._raise_for_status(resp)
            job = resp.json()
            if job["status"] == "completed":
                result = job.get("result", {})
                if full_response:
                    return result if isinstance(result, dict) else {}
                return result.get("data", result) if isinstance(result, dict) else {}
            if job["status"] == "failed":
                raise FetchError(f"Job {job_id} failed")
            await asyncio.sleep(POLL_INTERVAL)
        raise TimeoutError(f"Job {job_id} timed out after {MAX_POLL_SECONDS}s")
