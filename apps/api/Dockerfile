FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy workspace files needed for dependency resolution
COPY pyproject.toml uv.lock* ./
COPY packages/core ./packages/core
COPY apps/api ./apps/api

# Install only api and its dependencies
RUN uv sync --frozen --package datask-api --no-dev

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/apps/api/src:/app/packages/core/src

EXPOSE 8000

CMD ["uv", "run", "--package", "datask-api", "uvicorn", "datask_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
