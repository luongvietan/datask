# -*- coding: utf-8 -*-
"""
Layer 1 fetch task — runs inside RQ worker.
Uses Scrapling to bypass anti-bot and return clean Markdown.
"""
from __future__ import annotations

import hashlib
import os
import socket
import time
from datetime import UTC, datetime
from ipaddress import ip_address
from urllib.parse import urlparse

import redis as sync_redis
import structlog
from datask_core.models import ContentType
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

# Module-level Redis connection (reused across calls in the same worker process)
_redis_client: sync_redis.Redis | None = None


def _get_redis() -> sync_redis.Redis:
    global _redis_client
    if _redis_client is None:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = sync_redis.from_url(redis_url, decode_responses=True)
    return _redis_client


# SSRF protection — private IP ranges
_PRIVATE_PREFIXES = (
    "10.",
    "192.168.",
    "172.16.",
    "172.17.",
    "172.18.",
    "172.19.",
    "172.20.",
    "172.21.",
    "172.22.",
    "172.23.",
    "172.24.",
    "172.25.",
    "172.26.",
    "172.27.",
    "172.28.",
    "172.29.",
    "172.30.",
    "172.31.",
    "0.",
    "169.254.",
    "::1",
    "fc00:",
    "fd00:",
    "fe80:",
)


def _is_safe_url(url: str) -> bool:
    """
    SSRF protection: reject private IP ranges, localhost, and non-HTTP schemes.
    Performs DNS resolution to block SSRF via DNS rebinding.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = (parsed.hostname or "").lower()

        if hostname in ("localhost", ""):
            return False

        if any(hostname.startswith(p) for p in _PRIVATE_PREFIXES):
            return False

        # DNS resolution to catch SSRF via DNS rebinding
        try:
            resolved = socket.gethostbyname(hostname)
            addr = ip_address(resolved)
            if addr.is_private or addr.is_loopback or addr.is_link_local:
                return False
        except (socket.gaierror, ValueError):
            # DNS failure or IPv6 parse error — allow (will fail at fetch time)
            pass

        return True
    except Exception:
        return False


def _get_cache_key(url: str) -> str:
    return f"fetch:cache:{hashlib.sha256(url.encode()).hexdigest()[:16]}"


def _try_get_cache(url: str) -> str | None:
    """Check Redis cache for this URL."""
    try:
        return _get_redis().get(_get_cache_key(url))
    except Exception:
        return None


def _set_cache(url: str, content: str, ttl: int = 60) -> None:
    """Cache content in Redis."""
    try:
        _get_redis().setex(_get_cache_key(url), ttl, content)
    except Exception:
        pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def _scrape_with_scrapling(url: str) -> str:
    """
    Strategy router: try AsyncFetcher (fast, <2s) first.
    If Cloudflare challenge detected → fallback to StealthyFetcher.
    Returns raw HTML.
    """
    from scrapling.fetchers import AsyncFetcher, StealthyFetcher  # type: ignore[import]

    proxy_url = os.environ.get("BRIGHTDATA_PROXY_URL", "")

    try:
        fetcher = AsyncFetcher(proxy=proxy_url if proxy_url else None)
        page = fetcher.fetch(url)
        html = page.html_content

        cf_indicators = [
            "cf-mitigated",
            "cloudflare",
            "cf_chl_opt",
            "challenge-platform",
            "_cf_chl_",
        ]
        if any(ind in html.lower() for ind in cf_indicators) or page.status_code in (403, 503):
            raise ValueError("Cloudflare challenge detected, falling back to StealthyFetcher")

        return html
    except Exception as e:
        logger.info("async_fetcher_fallback", url=url, reason=str(e)[:100])

    fetcher_stealthy = StealthyFetcher(proxy=proxy_url if proxy_url else None)
    page = fetcher_stealthy.fetch(url)
    return page.html_content


def _html_to_markdown(html: str) -> str:
    """Convert HTML → clean Markdown."""
    try:
        import markdownify  # type: ignore[import]

        return markdownify.markdownify(html, heading_style="ATX", strip=["script", "style"])
    except ImportError:
        from html.parser import HTMLParser

        class _Stripper(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self._parts: list[str] = []

            def handle_data(self, data: str) -> None:
                self._parts.append(data)

            def get_text(self) -> str:
                return " ".join(self._parts)

        stripper = _Stripper()
        stripper.feed(html)
        return stripper.get_text()


def run_fetch(
    url: str,
    account_id: str | None = None,
    api_key_id: str | None = None,
) -> dict:
    """
    RQ task entry point.
    account_id/api_key_id used for usage tracking when present.
    Returns dict matching FetchResponse schema.
    """
    log = logger.bind(url=url)
    start_ms = int(time.time() * 1000)

    if not _is_safe_url(url):
        raise ValueError(f"URL blocked for security reasons: {url}")

    cached = _try_get_cache(url)
    if cached:
        log.info("fetch_cache_hit")
        return {
            "content": cached,
            "content_type": ContentType.MARKDOWN,
            "fetched_at": datetime.now(UTC).isoformat(),
            "url": url,
        }

    log.info("fetch_start")
    success = False
    error_code = None
    markdown = ""

    try:
        html = _scrape_with_scrapling(url)
        markdown = _html_to_markdown(html)
        success = True
        _set_cache(url, markdown, ttl=60)
        log.info("fetch_complete", markdown_length=len(markdown))
    except Exception as e:
        error_code = "fetch_failed"
        log.error("fetch_error", error=str(e))
        raise

    response_time_ms = int(time.time() * 1000) - start_ms

    if account_id:
        from datask_worker.usage_tracker import record_usage
        record_usage(
            account_id=account_id,
            api_key_id=api_key_id,
            url=url,
            layer=1,
            success=success,
            credits_used=1,
            response_time_ms=response_time_ms,
            error_code=error_code,
        )

    return {
        "content": markdown,
        "content_type": ContentType.MARKDOWN,
        "fetched_at": datetime.now(UTC).isoformat(),
        "url": url,
    }
