# -*- coding: utf-8 -*-
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from datask_core.config import get_settings
from datask_core.models import ErrorCode, ErrorResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from datask_api.middleware.request_context import RequestContextMiddleware
from datask_api.routes import auth, billing, extract, fetch, health, jobs, keys, webhooks

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logger.info("startup", env=settings.app_env)

    # Khởi động Stripe usage reporter scheduler (chỉ khi Stripe key có mặt)
    if settings.stripe_secret_key:
        from datask_api.services.usage_reporter import start_usage_reporter_scheduler
        start_usage_reporter_scheduler()

    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Datask API",
        description="Web Data API for AI Agents — Ask for any web data. Get it structured.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # In production use the configured base URL; in dev allow localhost ports
    allow_origins = (
        [settings.base_url]
        if settings.is_production
        else [settings.base_url, "http://localhost:3000", "http://localhost:3001"]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Datask-Async", "X-Request-Id"],
    )
    app.add_middleware(RequestContextMiddleware)

    app.include_router(health.router, tags=["System"])
    app.include_router(fetch.router, prefix="/v1", tags=["Layer 1 — Fetch"])
    app.include_router(extract.router, prefix="/v1", tags=["Layer 2/3 — Extract"])
    app.include_router(keys.router, prefix="/v1", tags=["API Keys"])
    app.include_router(billing.router, prefix="/v1", tags=["Billing"])
    app.include_router(auth.router, prefix="/v1", tags=["Auth"])
    app.include_router(jobs.router, prefix="/v1", tags=["Async Jobs"])
    app.include_router(webhooks.router, prefix="/v1", tags=["Webhooks"])

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request, exc):  # type: ignore[no-untyped-def]
        logger.exception("unhandled_error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred.",
            ).model_dump(),
        )

    return app


app = create_app()
