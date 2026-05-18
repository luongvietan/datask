# -*- coding: utf-8 -*-
"""
Auth routes:
- POST /v1/auth/oauth/upsert — upsert account + oauth_account khi NextAuth callback
- POST /v1/auth/session-key — issue short-lived dashboard JWT (dtsk_sess_*)
"""
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from datask_core.config import get_settings
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from jose import jwt
from pydantic import BaseModel, EmailStr

from datask_api.db.repositories import accounts as accounts_repo
from datask_api.db.session import get_session_factory

logger = structlog.get_logger()
router = APIRouter()

SESSION_KEY_PREFIX = "dtsk_sess_"
SESSION_JWT_ALGORITHM = "HS256"
SESSION_TTL_SECONDS = 60 * 60 * 24  # 24h


class OAuthUpsertRequest(BaseModel):
    provider: str           # google | github
    provider_account_id: str
    email: EmailStr
    name: str | None = None


class SessionKeyRequest(BaseModel):
    account_id: str


@router.post(
    "/auth/oauth/upsert",
    summary="Upsert account from OAuth provider callback (internal — called by NextAuth)",
)
async def oauth_upsert(body: OAuthUpsertRequest) -> JSONResponse:
    """
    Được gọi từ NextAuth server-side callback.
    Tạo hoặc tìm account theo email, liên kết OAuth provider.
    Returns account_id để NextAuth đưa vào JWT.
    """
    factory = get_session_factory()
    async with factory() as session:
        # Tìm theo OAuth provider trước
        account = await accounts_repo.get_by_oauth(
            session, body.provider, body.provider_account_id
        )

        if account is None:
            # Tìm theo email
            account = await accounts_repo.get_by_email(session, body.email)

        if account is None:
            # Tạo account mới
            account = await accounts_repo.create(
                session, email=body.email, email_verified=True
            )

        # Upsert OAuth link
        await accounts_repo.upsert_oauth(
            session,
            account_id=account.id,
            provider=body.provider,
            provider_account_id=body.provider_account_id,
        )
        await session.commit()

        logger.info("oauth_upsert", account_id=account.id, provider=body.provider)

        return JSONResponse(
            content={
                "account_id": account.id,
                "email": account.email,
                "tier": account.tier,
            }
        )


@router.post(
    "/auth/session-key",
    summary="Issue a short-lived dashboard session JWT",
)
async def issue_session_key(body: SessionKeyRequest) -> JSONResponse:
    """
    Phát JWT dtsk_sess_* cho dashboard.
    Frontend dùng key này để gọi /v1/keys, /v1/billing/*, etc.
    TTL: 24h.
    """
    settings = get_settings()
    factory = get_session_factory()

    async with factory() as session:
        account = await accounts_repo.get_by_id(session, body.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": account.id,
        "account_id": account.id,
        "email": account.email,
        "tier": account.tier,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=SESSION_TTL_SECONDS)).timestamp()),
        "jti": secrets.token_hex(8),
        "type": "session",
    }

    token = jwt.encode(payload, settings.app_secret_key, algorithm=SESSION_JWT_ALGORITHM)
    session_key = f"{SESSION_KEY_PREFIX}{token}"

    return JSONResponse(
        content={
            "session_key": session_key,
            "expires_in": SESSION_TTL_SECONDS,
        }
    )
