# -*- coding: utf-8 -*-
"""
Compare Datask vs Firecrawl benchmark results.

Usage:
    uv run python benchmarks/turnstile-2026/compare.py
    uv run python benchmarks/turnstile-2026/compare.py --datask results/datask_results.json --firecrawl results/firecrawl_results.json

Reads results JSON from both providers and outputs a comparison table + JSON summary.

Success criteria: HTTP 200 + content > 500 chars (Markdown).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR / "results"

DATASK_CREDITS_PER_REQUEST = 1
DATASK_CREDITS_TO_USD = 0.001
FIRECRAWL_CREDITS_PER_REQUEST = 1
FIRECRAWL_CREDITS_TO_USD = 0.001


def load_results(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cost_per_1k_success(success_count: int, credits_per_req: float, credits_to_usd: float) -> float | None:
    if success_count == 0:
        return None
    total_credits = success_count * credits_per_req
    total_usd = total_credits * credits_to_usd
    return round(total_usd / success_count * 1000, 2)


def print_comparison(datask: dict, firecrawl: dict) -> None:
    ds = datask["summary"]
    fs = firecrawl["summary"]

    ds_cost = cost_per_1k_success(
        ds["success"], DATASK_CREDITS_PER_REQUEST, DATASK_CREDITS_TO_USD
    )
    fs_cost = cost_per_1k_success(
        fs["success"], FIRECRAWL_CREDITS_PER_REQUEST, FIRECRAWL_CREDITS_TO_USD
    )

    print()
    print("=" * 72)
    print(f"  {'Metric':<28} {'Datask':>18} {'Firecrawl':>18}")
    print("=" * 72)
    print(f"  {'Total sites':<28} {ds['total']:>18} {fs['total']:>18}")
    print(f"  {'Successful fetches':<28} {ds['success']:>18} {fs['success']:>18}")
    print(f"  {'Success rate':<28} {ds['success_rate']:>17.1f}% {fs['success_rate']:>17.1f}%")
    print(f"  {'Latency p50 (ms)':<28} {str(ds['latency_p50_ms'] or 'N/A'):>18} {str(fs['latency_p50_ms'] or 'N/A'):>18}")
    print(f"  {'Latency p95 (ms)':<28} {str(ds['latency_p95_ms'] or 'N/A'):>18} {str(fs['latency_p95_ms'] or 'N/A'):>18}")
    print(f"  {'Latency mean (ms)':<28} {str(ds['latency_mean_ms'] or 'N/A'):>18} {str(fs['latency_mean_ms'] or 'N/A'):>18}")
    print(f"  {'Avg content length':<28} {ds['avg_content_length']:>18} {fs['avg_content_length']:>18}")
    print(f"  {'Cost per 1K success (USD)':<28} {f'${ds_cost}' if ds_cost else 'N/A':>18} {f'${fs_cost}' if fs_cost else 'N/A':>18}")
    print(f"  {'Total time (s)':<28} {ds.get('total_time_seconds', 'N/A'):>18} {fs.get('total_time_seconds', 'N/A'):>18}")
    print("=" * 72)

    all_cats = sorted(
        set(list(ds.get("by_category", {}).keys()) + list(fs.get("by_category", {}).keys()))
    )
    if all_cats:
        print()
        print("  Per-category breakdown:")
        print(f"  {'Category':<16} {'Datask':>12} {'Firecrawl':>12}")
        print("  " + "-" * 42)
        for cat in all_cats:
            dc = ds.get("by_category", {}).get(cat, {})
            fc = fs.get("by_category", {}).get(cat, {})
            d_rate = f"{dc.get('success_rate', 0):.0f}%" if dc else "N/A"
            f_rate = f"{fc.get('success_rate', 0):.0f}%" if fc else "N/A"
            d_detail = f"{dc.get('success', 0)}/{dc.get('total', 0)}" if dc else "-"
            f_detail = f"{fc.get('success', 0)}/{fc.get('total', 0)}" if fc else "-"
            print(f"  {cat:<16} {d_rate} ({d_detail}):>12 {f_rate} ({f_detail}):>12")
        print()

    print_per_site_diff(datask, firecrawl)


def print_per_site_diff(datask: dict, firecrawl: dict) -> None:
    ds_map = {r["url"]: r for r in datask["results"]}
    fs_map = {r["url"]: r for r in firecrawl["results"]}
    all_urls = list(ds_map.keys())

    divergent = []
    for url in all_urls:
        dr = ds_map.get(url, {})
        fr = fs_map.get(url, {})
        if dr.get("success") != fr.get("success"):
            divergent.append({
                "url": url,
                "name": dr.get("name", fr.get("name", "?")),
                "datask_success": dr.get("success", False),
                "firecrawl_success": fr.get("success", False),
                "datask_latency": dr.get("latency_ms", 0),
                "firecrawl_latency": fr.get("latency_ms", 0),
            })

    if divergent:
        print(f"  Divergent results ({len(divergent)} sites):")
        print(f"  {'Site':<30} {'Datask':>10} {'Firecrawl':>10}")
        print("  " + "-" * 52)
        for d in divergent:
            ds_status = "OK" if d["datask_success"] else "FAIL"
            fs_status = "OK" if d["firecrawl_success"] else "FAIL"
            print(f"  {d['name']:<30} {ds_status:>10} {fs_status:>10}")
        print()


def build_comparison_json(datask: dict, firecrawl: dict) -> dict:
    ds = datask["summary"]
    fs = firecrawl["summary"]

    ds_cost = cost_per_1k_success(
        ds["success"], DATASK_CREDITS_PER_REQUEST, DATASK_CREDITS_TO_USD
    )
    fs_cost = cost_per_1k_success(
        fs["success"], FIRECRAWL_CREDITS_PER_REQUEST, FIRECRAWL_CREDITS_TO_USD
    )

    return {
        "benchmark": "turnstile-2026",
        "datask": {
            "run_at": datask.get("run_at"),
            "config": datask.get("config"),
            "summary": ds,
            "cost_per_1k_success_usd": ds_cost,
        },
        "firecrawl": {
            "run_at": firecrawl.get("run_at"),
            "config": firecrawl.get("config"),
            "summary": fs,
            "cost_per_1k_success_usd": fs_cost,
        },
        "verdict": _verdict(ds, fs),
    }


def _verdict(ds: dict, fs: dict) -> dict:
    verdict = {}
    if ds["success_rate"] > fs["success_rate"]:
        verdict["success_rate"] = "datask"
    elif fs["success_rate"] > ds["success_rate"]:
        verdict["success_rate"] = "firecrawl"
    else:
        verdict["success_rate"] = "tie"

    ds_p50 = ds.get("latency_p50_ms")
    fs_p50 = fs.get("latency_p50_ms")
    if ds_p50 and fs_p50:
        verdict["latency_p50"] = "datask" if ds_p50 < fs_p50 else "firecrawl" if fs_p50 < ds_p50 else "tie"

    return verdict


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Datask vs Firecrawl benchmark results")
    parser.add_argument("--datask", default=str(RESULTS_DIR / "datask_results.json"))
    parser.add_argument("--firecrawl", default=str(RESULTS_DIR / "firecrawl_results.json"))
    parser.add_argument("--output", default=str(RESULTS_DIR / "comparison.json"))
    args = parser.parse_args()

    datask_path = Path(args.datask)
    firecrawl_path = Path(args.firecrawl)

    if not datask_path.exists():
        print(f"Error: Datask results not found at {datask_path}", file=sys.stderr)
        print("Run: uv run python benchmarks/turnstile-2026/run_datask.py", file=sys.stderr)
        sys.exit(1)

    if not firecrawl_path.exists():
        print(f"Error: Firecrawl results not found at {firecrawl_path}", file=sys.stderr)
        print("Run: uv run python benchmarks/turnstile-2026/run_firecrawl.py", file=sys.stderr)
        sys.exit(1)

    datask = load_results(datask_path)
    firecrawl = load_results(firecrawl_path)

    print_comparison(datask, firecrawl)

    comparison = build_comparison_json(datask, firecrawl)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    print(f"Comparison saved to {output_path}")


if __name__ == "__main__":
    main()
