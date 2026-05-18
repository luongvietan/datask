# -*- coding: utf-8 -*-
"""
API key + session authentication dependency.
Chấp nhận:
  - dtsk_live_* : API key (bcrypt hash trong DB, Redis cache)
  - dtsk_sess_* : Dashboard session JWT (short-lived, 24h)
"""
from typing import Any

import structlog
from datask_core.config import get_settings
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

logger = structlog.get_logger()
bearer = HTTPBearer(auto_error=False)

SESSION_KEY_PREFIX = "dtsk_sess_"
SESSION_JWT_ALGORITHM = "HS256"


async def get_current_key(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer),  # noqa: B008
) -> dict[str, Any]:
    """
    Validate Bearer token. Returns key record dict on success.
    Accepts: dtsk_live_* (API key) và dtsk_sess_* (dashboard session JWT).
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail={"error": "invalid_api_key", "message": "Authorization header missing or malformed."},
        )

    raw_key = credentials.credentials

    # dtsk_sess_* — Dashboard JWT session key
    if raw_key.startswith(SESSION_KEY_PREFIX):
        return await _validate_session_key(raw_key)

    # dtsk_live_* — API key (bcrypt, DB-backed)
    if raw_key.startswith("dtsk_live_"):
        return await _validate_api_key(raw_key)

    raise HTTPException(
        status_code=401,
        detail={"error": "invalid_api_key", "message": "Unrecognized key format."},
    )


async def _validate_api_key(raw_key: str) -> dict[str, Any]:
    from datask_api.services.api_keys import validate_api_key

    key_record = await validate_api_key(raw_key)
    if key_record is None:
        raise HTTPException(
            status_code=401,
            detail={"error": "invalid_api_key", "message": "Invalid or revoked API key."},
        )
    return key_record


async def _validate_session_key(session_key: str) -> dict[str, Any]:
    """Validate dtsk_sess_* JWT và trả về record tương thích."""
    token = session_key[len(SESSION_KEY_PREFIX):]
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.app_secret_key,
            algorithms=[SESSION_JWT_ALGORITHM],
        )
    except JWTError as e:
        logger.warning("session_key_invalid", error=str(e))
        raise HTTPException(
            status_code=401,
            detail={"error": "invalid_api_key", "message": "Invalid or expired session."},
        )

    if payload.get("type") != "session":
        raise HTTPException(
            status_code=401,
            detail={"error": "invalid_api_key", "message": "Invalid session token type."},
        )

    return {
        "id": f"sess_{payload['jti']}",
        "account_id": payload["account_id"],
        "label": "dashboard-session",
        "key_prefix": "dtsk_sess_",
        "is_active": True,
        "tier": payload.get("tier", "free"),
        "stripe_subscription_id": None,
        "is_session": True,
    }
