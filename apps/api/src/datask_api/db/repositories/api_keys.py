# -*- coding: utf-8 -*-
"""Repository cho bảng api_keys."""
import hashlib
import secrets
from datetime import UTC, datetime
from typing import Any

import bcrypt as _bcrypt

from datask_api.models.db import ApiKey
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


def _hash_key(raw_key: str) -> str:
    """
    Hash API key: SHA-256 prehash → bcrypt (bcrypt trực tiếp, không qua passlib).
    SHA-256 trước để tránh 72-byte bcrypt limit.
    """
    sha = hashlib.sha256(raw_key.encode("utf-8")).digest()
    return _bcrypt.hashpw(sha, _bcrypt.gensalt(rounds=12)).decode("utf-8")


def _verify_key(raw_key: str, key_hash: str) -> bool:
    """Verify API key bằng SHA-256 prehash + bcrypt."""
    sha = hashlib.sha256(raw_key.encode("utf-8")).digest()
    return _bcrypt.checkpw(sha, key_hash.encode("utf-8"))

KEY_PREFIX_LENGTH = 20  # "dtsk_live_" + 10 chars


def generate_raw_key() -> str:
    return f"dtsk_live_{secrets.token_hex(32)}"


async def create(
    session: AsyncSession,
    account_id: str,
    label: str = "default",
) -> dict[str, Any]:
    """
    Tạo API key mới.
    Returns dict có full raw key (chỉ trả 1 lần, không lưu plaintext).
    """
    raw_key = generate_raw_key()
    key_hash = _hash_key(raw_key)
    key_prefix = raw_key[:KEY_PREFIX_LENGTH]
    key_id = secrets.token_hex(8)

    api_key = ApiKey(
        id=key_id,
        account_id=account_id,
        label=label,
        key_hash=key_hash,
        key_prefix=key_prefix,
        is_active=True,
    )
    session.add(api_key)
    await session.flush()

    return {
        "id": key_id,
        "label": label,
        "key": raw_key,
        "key_preview": key_prefix + "...",
        "created_at": api_key.created_at.isoformat() if api_key.created_at else datetime.now(UTC).isoformat(),
        "is_active": True,
    }


async def list_by_account(session: AsyncSession, account_id: str) -> list[dict[str, Any]]:
    result = await session.execute(
        select(ApiKey)
        .where(ApiKey.account_id == account_id)
        .order_by(ApiKey.created_at.desc())
    )
    keys = result.scalars().all()
    return [
        {
            "id": k.id,
            "label": k.label,
            "key_preview": k.key_prefix + "...",
            "created_at": k.created_at.isoformat(),
            "is_active": k.is_active,
        }
        for k in keys
    ]


async def get_by_id(session: AsyncSession, key_id: str) -> ApiKey | None:
    result = await session.execute(
        select(ApiKey).options(joinedload(ApiKey.account)).where(ApiKey.id == key_id)
    )
    return result.scalar_one_or_none()


async def revoke(session: AsyncSession, key_id: str, account_id: str) -> str | None:
    """Revoke key; trả key_prefix nếu thành công, None nếu không tìm thấy."""
    result = await session.execute(
        update(ApiKey)
        .where(ApiKey.id == key_id, ApiKey.account_id == account_id)
        .values(is_active=False)
        .returning(ApiKey.key_prefix)
    )
    return result.scalar_one_or_none()


async def get_active_by_prefix(session: AsyncSession, prefix: str) -> list[ApiKey]:
    """Lấy các key active theo prefix (để verify bcrypt)."""
    result = await session.execute(
        select(ApiKey)
        .options(joinedload(ApiKey.account))
        .where(ApiKey.key_prefix == prefix, ApiKey.is_active == True)  # noqa: E712
    )
    return list(result.scalars().all())


async def touch_last_used(session: AsyncSession, key_id: str) -> None:
    await session.execute(
        update(ApiKey).where(ApiKey.id == key_id).values(last_used_at=datetime.now(UTC))
    )
