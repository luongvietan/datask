FROM python:3.12-slim

WORKDIR /app

# Playwright system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* ./
COPY packages/core ./packages/core
COPY apps/worker ./apps/worker

RUN uv sync --frozen --package datask-worker --no-dev

# Install Playwright browsers
RUN uv run --package datask-worker playwright install chromium

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/apps/worker/src:/app/packages/core/src

CMD ["uv", "run", "--package", "datask-worker", "python", "-m", "datask_worker.main"]
