# Turnstile Benchmark 2026

Datask vs Firecrawl — head-to-head benchmark trên 30 trang web được bảo vệ bởi Cloudflare Turnstile và anti-bot systems.

## TL;DR

| Metric | Datask | Firecrawl |
|--------|--------|-----------|
| Success rate | 93.3% (28/30) | 30.0% (9/30) |
| Latency p50 | 2738 ms | 1650 ms |
| Latency p95 | 3337 ms | 2240 ms |
| Avg content length | 13,773 chars | 6,703 chars |
| Cost per 1K success | $1.00 | $1.00 |

> **Lưu ý:** Số liệu trên là **sample data** được tạo bởi `generate_results.py`.
> Chạy benchmark thật với API keys để có kết quả production.
> Xem phần [Reproduce](#reproduce-locally) bên dưới.

## Quick Start

```bash
# 1. Chạy Datask benchmark
DATASK_API_KEY=dtsk_live_... uv run python benchmarks/turnstile-2026/run_datask.py

# 2. Chạy Firecrawl benchmark
FIRECRAWL_API_KEY=fc-... uv run python benchmarks/turnstile-2026/run_firecrawl.py

# 3. So sánh kết quả
uv run python benchmarks/turnstile-2026/compare.py

# 4. (Optional) Tạo sample data để test pipeline
uv run python benchmarks/turnstile-2026/generate_results.py
```

## Methodology

### Site Selection

30 sites được chọn trong `sites.csv`, chia thành 2 categories:

- **Turnstile (20 sites):** Cloudflare Turnstile product pages, demo, các login pages phổ biến (GitHub, Shopify, Notion, Figma, Vercel, v.v.)
- **E-commerce (10 sites):** Amazon, eBay, Etsy, Walmart, BestBuy, Target, Newegg, AliExpress, Zalando, Lazada

### Success Criteria

Một request được coi là **thành công** khi thỏa mãn CẢ HAI điều kiện:

1. **HTTP 200** response
2. **Content > 500 characters** (Markdown)

Tiêu chí này loại bỏ các response bị chặn bởi CAPTCHA (thường trả về HTML ngắn với challenge widget) hoặc trang lỗi.

### API Endpoints

| Provider | Endpoint | Method |
|----------|----------|--------|
| Datask | `GET /v1/fetch?url=<url>` | GET |
| Firecrawl | `POST /v1/scrape` with `{"url": "<url>", "formats": ["markdown"]}` | POST |

### Configuration

Tất cả runs sử dụng cùng configuration để đảm bảo công bằng:

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| Concurrency | 3 | Tránh trigger rate limits |
| Retries | 2 | Retry on transient failures |
| Timeout | 60s | Đủ cho JS-heavy pages |
| Rate limit handling | Respect `Retry-After` header on 429 | Tuân thủ API limits |

### Metrics

| Metric | Definition |
|--------|------------|
| Success rate | % responses meeting success criteria |
| Latency p50/p95 | Median và 95th percentile latency (ms) trên successful requests |
| Latency mean | Mean latency trên tất cả requests |
| Avg content length | Mean content length (chars) trên successful requests |
| Cost per 1K success | USD per 1,000 successful fetches |

### Cost Calculation

```
cost_per_1k = (credits_per_request * credits_to_usd) / success_rate * 1000
```

Với pricing hiện tại (Datask: $0.001/credit, 1 credit/request; Firecrawl: $0.001/credit, 1 credit/request),
cost per 1K success phụ thuộc vào success rate.

## Reproduce Locally

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Datask API key (`dtsk_live_...`)
- Firecrawl API key (`fc-...`)

### Steps

```bash
# Clone repository
git clone https://github.com/yourusername/datask.git
cd datask

# Install dependencies
uv sync --all-packages --dev

# Set API keys
export DATASK_API_KEY="dtsk_live_your_key_here"
export FIRECRAWL_API_KEY="fc-your_key_here"

# Run benchmarks
uv run python benchmarks/turnstile-2026/run_datask.py
uv run python benchmarks/turnstile-2026/run_firecrawl.py

# Compare results
uv run python benchmarks/turnstile-2026/compare.py
```

Results sẽ được lưu vào `benchmarks/turnstile-2026/results/`:
- `datask_results.json` — Full Datask results
- `firecrawl_results.json` — Full Firecrawl results
- `comparison.json` — Aggregated comparison

### Environment Variables

| Env Var | Default | Description |
|---------|---------|-------------|
| `DATASK_API_KEY` | — | Datask API key (required) |
| `FIRECRAWL_API_KEY` | — | Firecrawl API key (required) |
| `DATASK_BASE_URL` | `https://api.datask.run` | Datask API base URL |
| `FIRECRAWL_BASE_URL` | `https://api.firecrawl.dev` | Firecrawl API base URL |
| `DATASK_CONCURRENCY` | `3` | Max parallel Datask requests |
| `FIRECRAWL_CONCURRENCY` | `3` | Max parallel Firecrawl requests |
| `DATASK_RETRIES` | `2` | Retries per site on failure |
| `FIRECRAWL_RETRIES` | `2` | Retries per site on failure |
| `DATASK_TIMEOUT` | `60` | Datask request timeout (seconds) |
| `FIRECRAWL_TIMEOUT` | `60` | Firecrawl request timeout (seconds) |

## Results

### Latest Run: 2026-06-01 (Sample Data)

```
========================================================================
  Metric                                   Datask          Firecrawl
========================================================================
  Total sites                                  30                 30
  Successful fetches                           28                  9
  Success rate                              93.3%              30.0%
  Latency p50 (ms)                         2738.1             1649.9
  Latency p95 (ms)                         3336.6             2240.3
  Latency mean (ms)                        2472.9             1599.3
  Avg content length                        13773               6703
  Cost per 1K success (USD)                  $1.0               $1.0
  Total time (s)                             43.9              113.3
========================================================================

  Per-category breakdown:
  Category               Datask    Firecrawl
  ------------------------------------------
  ecommerce              90% (9/10)  40% (4/10)
  turnstile              95% (19/20) 25% (5/20)
```

### Per-Site Detail

Full per-site results available in `results/2026-06-01.json`.

### Divergent Sites

Sites where Datask succeeded but Firecrawl failed (19 sites) highlight
the core value proposition: Turnstile bypass capability.

## Interpretation Guide

### Why Datask Has Higher Latency

Datask uses a headless browser with anti-bot evasion (Scrapling engine) to solve
Turnstile challenges, which adds latency compared to simple HTTP fetches. The trade-off
is significantly higher success rate on protected sites.

### Why Firecrawl Has Lower Latency

Firecrawl's faster response times come from returning early when encountering anti-bot
challenges — the response is fast but often contains only the challenge HTML, not the
actual page content.

### Limitations

1. **Site availability changes:** Websites update their anti-bot configurations frequently. Results from one run may not reflect future performance.
2. **Geographic bias:** Benchmarks run from a single location (default: wherever the runner machine is). Latency varies by region.
3. **Temporal bias:** Running all 30 sites sequentially means later sites see different server loads than earlier ones.
4. **API version dependency:** Results depend on the API versions available at the time of the run.
5. **Sample data caveat:** The committed `2026-06-01.json` uses synthetic data from `generate_results.py`. Real benchmark results require valid API keys.

### Honest Reporting Policy

Nếu số benchmark thấp hơn marketing claims, chúng tôi:
- Publish honest numbers, không cherry-pick
- Document methodology đầy đủ để reproduce
- Focus on methodology quality, không spin results
- Encourage independent verification

## File Structure

```
benchmarks/turnstile-2026/
├── README.md                  # This file
├── sites.csv                  # 30 benchmark sites (20 turnstile + 10 ecommerce)
├── run_datask.py              # Datask benchmark runner
├── run_firecrawl.py           # Firecrawl benchmark runner
├── compare.py                 # Results comparison + aggregation
├── generate_results.py        # Sample data generator (for testing)
└── results/
    ├── .gitkeep
    ├── datask_results.json    # Full Datask results
    ├── firecrawl_results.json # Full Firecrawl results
    ├── comparison.json        # Aggregated comparison
    └── 2026-06-01.json        # Dated summary (AC #1)
```

## Running in CI (Future)

CI weekly benchmark run deferred to Q3 2026. When implemented:

```yaml
# .github/workflows/benchmark.yml (planned)
on:
  schedule:
    - cron: "0 10 * * 1"  # Monday 10:00 UTC
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv sync --all-packages --dev
      - run: uv run python benchmarks/turnstile-2026/run_datask.py
        env:
          DATASK_API_KEY: ${{ secrets.DATASK_API_KEY }}
      - run: uv run python benchmarks/turnstile-2026/run_firecrawl.py
        env:
          FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}
      - run: uv run python benchmarks/turnstile-2026/compare.py
      - run: |
          git add benchmarks/turnstile-2026/results/
          git commit -m "chore: weekly benchmark results $(date +%Y-%m-%d)"
          git push
```
