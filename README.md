# Datask — Web Data API for AI Agents

> *"Ask for any web data. Get it structured."*

[![Turnstile Benchmark](https://img.shields.io/badge/Turnstile%20Success-93.3%25-brightgreen)](benchmarks/turnstile-2026/README.md)

Datask là Web Data API dành cho AI agents — kết hợp native Cloudflare Turnstile bypass, structured JSON output, và Natural Language extraction trong một API đơn giản, usage-based.

## Monorepo Structure

```
datask/
├── apps/
│   ├── api/                        # FastAPI HTTP API (Layer 1, 2, 3)
│   │   ├── src/datask_api/
│   │   │   ├── main.py             # App factory
│   │   │   ├── routes/             # fetch, extract, keys, billing, health
│   │   │   ├── middleware/auth.py  # Bearer API key auth
│   │   │   ├── services/           # rate_limiter, api_keys, job_queue, billing
│   │   │   └── models/db.py        # SQLAlchemy ORM (accounts, api_keys, usage)
│   │   └── Dockerfile
│   ├── worker/                     # Scrapling RQ worker (anti-bot engine)
│   │   ├── src/datask_worker/
│   │   │   ├── main.py             # RQ worker entrypoint
│   │   │   └── tasks/              # fetch.py (L1), extract.py (L2/L3)
│   │   └── Dockerfile
│   └── web/                        # Next.js 15 frontend
│       ├── src/
│       │   ├── app/
│       │   │   ├── (marketing)/    # Landing, Pricing, Docs
│       │   │   ├── (dashboard)/    # Dashboard, Keys, Billing, Usage
│       │   │   └── (auth)/         # Login, Register
│       │   ├── components/
│       │   │   ├── ui/             # Button, Card, Badge, Input, Skeleton
│       │   │   ├── marketing/      # HeroSection, FeaturesSection, PricingSection…
│       │   │   ├── dashboard/      # UsageStatsCards, RequestsChart, ApiKeysList…
│       │   │   └── layout/         # TopNav, Footer
│       │   ├── lib/api.ts          # REST API client
│       │   ├── hooks/              # useUsage, useApiKeys
│       │   └── types/index.ts      # Shared TypeScript types
│       ├── tailwind.config.ts      # Full design token system (docs/Design.md)
│       └── next.config.ts
├── packages/
│   ├── core/                       # Shared Python: Pydantic models, config
│   ├── sdk-py/                     # Python SDK — datask-py (Phase 2)
│   └── sdk-js/                     # TypeScript SDK — datask-js (Phase 2)
│       └── src/                    # DataskClient, types, error classes
├── infra/
│   ├── docker-compose.yml          # Local dev (API + Worker + Postgres + Redis)
│   └── railway.toml                # Railway deploy config
├── .github/workflows/ci.yml        # Lint + typecheck + tests
├── pyproject.toml                  # uv workspace root
└── .env.example
```

## Quick Start (Local Dev)

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (`pip install uv`)
- Docker + Docker Compose

### 1. Clone & setup environment

```bash
git clone https://github.com/yourusername/datask.git
cd datask
cp .env.example .env
# Edit .env — at minimum set DATABASE_URL and REDIS_URL
```

### 2. Install all dependencies

```bash
uv sync --all-packages --dev
```

### 3. Start infrastructure (Postgres + Redis)

```bash
docker compose -f infra/docker-compose.yml up postgres redis -d
```

### 4. Run the API

```bash
uv run --package datask-api uvicorn datask_api.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 5. Run the worker

```bash
uv run --package datask-worker python -m datask_worker.main
```

### 6. Test Layer 1

```bash
curl "http://localhost:8000/v1/fetch?url=https://example.com"
```

## API Layers

| Layer | Endpoint | Auth | Cost |
|-------|----------|------|------|
| Layer 1 | `GET /v1/fetch?url=` | None | Free |
| Layer 2 | `POST /v1/extract` + `schema` | API Key | $0.005/req |
| Layer 3 | `POST /v1/extract` + `prompt` | API Key | $0.008/req |

## Python SDK (Phase 2)

```python
import datask

client = datask.Client(api_key="dtsk_live_...")

# Layer 1 — free
content = client.fetch("https://example.com")

# Layer 2 — schema
data = client.extract(
    "https://shop.example.com/product",
    schema={"price": "number", "title": "string", "in_stock": "boolean"},
)

# Layer 3 — natural language
data = client.extract(
    "https://shop.example.com/product",
    prompt="Get me the product price, title, and whether it's in stock",
)
```

## Development Commands

```bash
# --- Backend (Python / uv) ---
uv run ruff check .                    # Lint all Python
uv run ruff format .                   # Format all Python
uv run mypy apps/api/src packages/core/src  # Type check
uv run pytest -v                       # Run tests

# --- Frontend (Next.js) ---
cd apps/web
npm install
npm run dev          # http://localhost:3000
npm run typecheck    # TypeScript strict check
npm run lint         # ESLint

# --- JS SDK ---
cd packages/sdk-js
npm install
npm run build        # tsup → dist/

# --- Full stack with Docker ---
docker compose -f infra/docker-compose.yml up
```

## Deployment (Railway)

Railway auto-deploys from `main` branch using `infra/railway.toml`.

Set environment variables in Railway dashboard — see `.env.example` for required vars.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API | FastAPI + uvicorn |
| Anti-bot engine | Scrapling v0.4.6 |
| Job queue | Redis + RQ |
| Database | PostgreSQL + SQLAlchemy 2.0 |
| Billing | Stripe |
| LLM (Layer 3) | OpenAI GPT-4o-mini |
| Hosting | Railway |
| Package manager | uv workspace |
