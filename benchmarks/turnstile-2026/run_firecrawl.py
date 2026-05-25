# -*- coding: utf-8 -*-
"""
Firecrawl benchmark runner — fetches all sites from sites.csv via Firecrawl API.

Usage:
    FIRECRAWL_API_KEY=fc-... uv run python benchmarks/turnstile-2026/run_firecrawl.py

Env vars:
    FIRECRAWL_API_KEY   - required, Firecrawl API key
    FIRECRAWL_BASE_URL  - optional, defaults to https://api.firecrawl.dev
    FIRECRAWL_CONCURRENCY - optional, max parallel requests (default: 3)
    FIRECRAWL_RETRIES   - optional, retries per site on failure (default: 2)
    FIRECRAWL_TIMEOUT   - optional, request timeout in seconds (default: 60)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
SITES_CSV = SCRIPT_DIR / "sites.csv"
RESULTS_DIR = SCRIPT_DIR / "results"
MIN_CONTENT_LENGTH = 500


def load_sites() -> list[dict[str, str]]:
    sites = []
    with open(SITES_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sites.append(row)
    return sites


def scrape_single(
    client: httpx.Client,
    url: str,
    retries: int,
    timeout: float,
) -> dict:
    result: dict = {
        "url": url,
        "success": False,
        "status_code": None,
        "content_length": 0,
        "latency_ms": 0,
        "error": None,
        "retries_used": 0,
    }

    for attempt in range(retries + 1):
        if attempt > 0:
            result["retries_used"] = attempt
            time.sleep(1.0 * attempt)

        start = time.perf_counter()
        try:
            resp = client.post(
                "/v1/scrape",
                json={
                    "url": url,
                    "formats": ["markdown"],
                },
                timeout=timeout,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            result["latency_ms"] = round(elapsed_ms, 2)
            result["status_code"] = resp.status_code

            if resp.status_code == 200:
                data = resp.json()
                if data.get("success") and data.get("data"):
                    markdown = data["data"].get("markdown", "")
                    result["content_length"] = len(markdown)
                    result["success"] = len(markdown) >= MIN_CONTENT_LENGTH

                    if result["success"]:
                        result["error"] = None
                        break
                    else:
                        result["error"] = f"Content too short ({len(markdown)} chars < {MIN_CONTENT_LENGTH})"
                else:
                    result["error"] = f"API error: {data.get('error', 'unknown')}"
            elif resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "5"))
                result["error"] = f"Rate limited (retry after {retry_after}s)"
                time.sleep(retry_after)
            else:
                body = resp.text[:200]
                result["error"] = f"HTTP {resp.status_code}: {body}"

        except httpx.TimeoutException:
            elapsed_ms = (time.perf_counter() - start) * 1000
            result["latency_ms"] = round(elapsed_ms, 2)
            result["error"] = "Timeout"
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            result["latency_ms"] = round(elapsed_ms, 2)
            result["error"] = str(exc)

    return result


def run_benchmark(
    sites: list[dict[str, str]],
    base_url: str,
    api_key: str,
    concurrency: int,
    retries: int,
    timeout: float,
) -> list[dict]:
    results = []
    total = len(sites)

    with (
        httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        ) as client,
        ThreadPoolExecutor(max_workers=concurrency) as pool,
    ):
        futures = {
            pool.submit(scrape_single, client, site["url"], retries, timeout): site
            for site in sites
        }
        for i, future in enumerate(as_completed(futures), 1):
            site = futures[future]
            result = future.result()
            result["name"] = site["name"]
            result["category"] = site["category"]
            results.append(result)

            status = "OK" if result["success"] else "FAIL"
            print(f"  [{i:2d}/{total}] {status}  {result['latency_ms']:8.0f}ms  {site['name']}")

    return results


def compute_summary(results: list[dict]) -> dict:
    success_results = [r for r in results if r["success"]]
    failed_results = [r for r in results if not r["success"]]
    all_latencies = [r["latency_ms"] for r in results if r["latency_ms"] > 0]
    success_latencies = [r["latency_ms"] for r in success_results if r["latency_ms"] > 0]

    summary = {
        "total": len(results),
        "success": len(success_results),
        "failed": len(failed_results),
        "success_rate": round(len(success_results) / len(results) * 100, 1) if results else 0,
        "latency_p50_ms": round(statistics.median(success_latencies), 1) if success_latencies else None,
        "latency_p95_ms": round(sorted(success_latencies)[int(len(success_latencies) * 0.95)], 1) if len(success_latencies) > 1 else None,
        "latency_mean_ms": round(statistics.mean(all_latencies), 1) if all_latencies else None,
        "avg_content_length": round(statistics.mean([r["content_length"] for r in success_results])) if success_results else 0,
        "by_category": {},
    }

    categories = set(r["category"] for r in results)
    for cat in sorted(categories):
        cat_results = [r for r in results if r["category"] == cat]
        cat_success = [r for r in cat_results if r["success"]]
        summary["by_category"][cat] = {
            "total": len(cat_results),
            "success": len(cat_success),
            "success_rate": round(len(cat_success) / len(cat_results) * 100, 1) if cat_results else 0,
        }

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Firecrawl benchmark on Turnstile sites")
    parser.add_argument("--base-url", default=os.environ.get("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev"))
    parser.add_argument("--concurrency", type=int, default=int(os.environ.get("FIRECRAWL_CONCURRENCY", "3")))
    parser.add_argument("--retries", type=int, default=int(os.environ.get("FIRECRAWL_RETRIES", "2")))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("FIRECRAWL_TIMEOUT", "60")))
    parser.add_argument("--output", default=None, help="Output JSON file path")
    args = parser.parse_args()

    api_key = os.environ.get("FIRECRAWL_API_KEY", "")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY env var required", file=sys.stderr)
        sys.exit(1)

    sites = load_sites()
    print(f"Firecrawl Benchmark — {len(sites)} sites")
    print(f"Base URL: {args.base_url}")
    print(f"Concurrency: {args.concurrency} | Retries: {args.retries} | Timeout: {args.timeout}s")
    print("=" * 60)

    started = time.perf_counter()
    results = run_benchmark(sites, args.base_url, api_key, args.concurrency, args.retries, args.timeout)
    total_time = round(time.perf_counter() - started, 2)

    summary = compute_summary(results)
    summary["total_time_seconds"] = total_time

    print("=" * 60)
    print(f"Success: {summary['success']}/{summary['total']} ({summary['success_rate']}%)")
    print(f"Latency p50: {summary['latency_p50_ms']}ms | p95: {summary['latency_p95_ms']}ms")
    print(f"Total time: {total_time}s")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = args.output or str(RESULTS_DIR / "firecrawl_results.json")
    output = {
        "provider": "firecrawl",
        "run_at": datetime.now(UTC).isoformat(),
        "config": {
            "base_url": args.base_url,
            "concurrency": args.concurrency,
            "retries": args.retries,
            "timeout": args.timeout,
        },
        "summary": summary,
        "results": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
