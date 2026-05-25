# Turnstile Benchmark 2026

Datask vs Firecrawl — head-to-head trên 30 Turnstile-protected sites.

## Quick Start

```bash
# 1. Chạy Datask benchmark
DATASK_API_KEY=dtsk_live_... uv run python benchmarks/turnstile-2026/run_datask.py

# 2. Chạy Firecrawl benchmark
FIRECRAWL_API_KEY=fc-... uv run python benchmarks/turnstile-2026/run_firecrawl.py

# 3. So sánh kết quả
uv run python benchmarks/turnstile-2026/compare.py
```

## Success Criteria

- **HTTP 200** response
- **Content > 500 characters** (Markdown)

## Metrics

| Metric | Definition |
|--------|------------|
| Success rate | % responses meeting success criteria |
| Latency p50/p95 | Median and 95th percentile latency (ms) |
| Cost per 1K | USD per 1,000 successful fetches |

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `DATASK_API_KEY` | — | Datask API key (required) |
| `FIRECRAWL_API_KEY` | — | Firecrawl API key (required) |
| `DATASK_BASE_URL` | `https://api.datask.run` | Datask API base URL |
| `FIRECRAWL_BASE_URL` | `https://api.firecrawl.dev` | Firecrawl API base URL |
| `*_CONCURRENCY` | `3` | Max parallel requests |
| `*_RETRIES` | `2` | Retries per site on failure |
| `*_TIMEOUT` | `60` | Request timeout in seconds |

## Results

Kết quả JSON được lưu vào `results/`:
- `datask_results.json`
- `firecrawl_results.json`
- `comparison.json`

> Full methodology và analysis: xem story 4-2.
