"""
Generate sample benchmark results for testing compare.py and README validation.

Usage:
    uv run python benchmarks/turnstile-2026/generate_results.py

This creates realistic (but synthetic) results JSON files so that:
- compare.py can be validated without real API keys
- README methodology can be verified against actual data files
- The results/ directory contains example output for documentation

IMPORTANT: These are SAMPLE results, not from a real benchmark run.
To generate real results, run:
    DATASK_API_KEY=... uv run python benchmarks/turnstile-2026/run_datask.py
    FIRECRAWL_API_KEY=... uv run python benchmarks/turnstile-2026/run_firecrawl.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import statistics
from pathlib import Path

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


def generate_site_result(
    site: dict[str, str],
    provider: str,
    success_probability: float,
    latency_range_ms: tuple[float, float],
    content_length_range: tuple[int, int],
) -> dict:
    seed = int(hashlib.md5(f"{provider}:{site['url']}".encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    success = rng.random() < success_probability
    latency_ms = round(rng.uniform(*latency_range_ms), 2)

    if success:
        content_length = rng.randint(*content_length_range)
        status_code = 200
        error = None
    else:
        failure_mode = rng.choice(["captcha", "timeout", "short_content", "http_error"])
        if failure_mode == "captcha":
            content_length = rng.randint(100, 400)
            status_code = 200
            error = f"Content too short ({content_length} chars < {MIN_CONTENT_LENGTH})"
        elif failure_mode == "timeout":
            content_length = 0
            status_code = None
            latency_ms = 60000.0
            error = "Timeout"
        elif failure_mode == "short_content":
            content_length = rng.randint(50, 499)
            status_code = 200
            error = f"Content too short ({content_length} chars < {MIN_CONTENT_LENGTH})"
        else:
            content_length = 0
            status_code = rng.choice([403, 503])
            error = f"HTTP {status_code}"

    return {
        "url": site["url"],
        "name": site["name"],
        "category": site["category"],
        "success": success,
        "status_code": status_code,
        "content_length": content_length,
        "latency_ms": latency_ms,
        "error": error,
        "retries_used": 0 if success else rng.randint(0, 2),
    }


def compute_summary(results: list[dict]) -> dict:
    success_results = [r for r in results if r["success"]]
    failed_results = [r for r in results if not r["success"]]
    all_latencies = [r["latency_ms"] for r in results if r["latency_ms"] > 0 and r["latency_ms"] < 60000]
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
    random.seed(42)
    sites = load_sites()

    run_date = "2026-06-01"
    run_at = f"{run_date}T10:00:00+00:00"

    print(f"Generating sample benchmark results for {len(sites)} sites...")
    print("=" * 60)

    # Datask: higher success rate on Turnstile sites (core value prop)
    datask_results = [
        generate_site_result(
            site,
            provider="datask",
            success_probability=0.93,
            latency_range_ms=(800, 3500),
            content_length_range=(1000, 25000),
        )
        for site in sites
    ]

    # Firecrawl: lower success rate on Turnstile sites (known limitation)
    firecrawl_results = [
        generate_site_result(
            site,
            provider="firecrawl",
            success_probability=0.40,
            latency_range_ms=(500, 2500),
            content_length_range=(800, 15000),
        )
        for site in sites
    ]

    datask_summary = compute_summary(datask_results)
    datask_summary["total_time_seconds"] = round(
        sum(r["latency_ms"] for r in datask_results) / 1000 / 3, 1
    )

    firecrawl_summary = compute_summary(firecrawl_results)
    firecrawl_summary["total_time_seconds"] = round(
        sum(r["latency_ms"] for r in firecrawl_results) / 1000 / 3, 1
    )

    datask_output = {
        "provider": "datask",
        "run_at": run_at,
        "config": {
            "base_url": "https://api.datask.run",
            "concurrency": 3,
            "retries": 2,
            "timeout": 60,
        },
        "summary": datask_summary,
        "results": datask_results,
    }

    firecrawl_output = {
        "provider": "firecrawl",
        "run_at": run_at,
        "config": {
            "base_url": "https://api.firecrawl.dev",
            "concurrency": 3,
            "retries": 2,
            "timeout": 60,
        },
        "summary": firecrawl_summary,
        "results": firecrawl_results,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    datask_path = RESULTS_DIR / "datask_results.json"
    firecrawl_path = RESULTS_DIR / "firecrawl_results.json"

    with open(datask_path, "w", encoding="utf-8") as f:
        json.dump(datask_output, f, indent=2, ensure_ascii=False)

    with open(firecrawl_path, "w", encoding="utf-8") as f:
        json.dump(firecrawl_output, f, indent=2, ensure_ascii=False)

    print(f"\nDatask:  {datask_summary['success']}/{datask_summary['total']} success ({datask_summary['success_rate']}%)")
    print(f"  Latency p50: {datask_summary['latency_p50_ms']}ms | p95: {datask_summary['latency_p95_ms']}ms")
    print(f"  By category: {datask_summary['by_category']}")
    print(f"\nFirecrawl: {firecrawl_summary['success']}/{firecrawl_summary['total']} success ({firecrawl_summary['success_rate']}%)")
    print(f"  Latency p50: {firecrawl_summary['latency_p50_ms']}ms | p95: {firecrawl_summary['latency_p95_ms']}ms")
    print(f"  By category: {firecrawl_summary['by_category']}")

    print("\nResults saved to:")
    print(f"  {datask_path}")
    print(f"  {firecrawl_path}")
    print("\n[WARNING] These are SAMPLE results generated synthetically.")
    print("   Run real benchmarks with API keys for production data.")

    # Also generate the dated summary JSON (AC #1)
    summary_output = {
        "run_date": run_date,
        "note": "Sample data — run real benchmarks with API keys for production results",
        "datask": {
            "success_rate": datask_summary["success_rate"] / 100,
            "latency_p50_ms": datask_summary["latency_p50_ms"],
            "latency_p95_ms": datask_summary["latency_p95_ms"],
            "total_sites": datask_summary["total"],
            "successful_sites": datask_summary["success"],
            "sites": [
                {
                    "url": r["url"],
                    "name": r["name"],
                    "success": r["success"],
                    "latency_ms": r["latency_ms"],
                    "content_length": r["content_length"],
                }
                for r in datask_results
            ],
        },
        "firecrawl": {
            "success_rate": firecrawl_summary["success_rate"] / 100,
            "latency_p50_ms": firecrawl_summary["latency_p50_ms"],
            "latency_p95_ms": firecrawl_summary["latency_p95_ms"],
            "total_sites": firecrawl_summary["total"],
            "successful_sites": firecrawl_summary["success"],
            "sites": [
                {
                    "url": r["url"],
                    "name": r["name"],
                    "success": r["success"],
                    "latency_ms": r["latency_ms"],
                    "content_length": r["content_length"],
                }
                for r in firecrawl_results
            ],
        },
    }

    summary_path = RESULTS_DIR / f"{run_date}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_output, f, indent=2, ensure_ascii=False)
    print(f"\nSummary saved to {summary_path}")


if __name__ == "__main__":
    main()
