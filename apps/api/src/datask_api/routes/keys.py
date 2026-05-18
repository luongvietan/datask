# -*- coding: utf-8 -*-
"""API Key management — create, list, revoke."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

from datask_api.middleware.auth import get_current_key
from datask_api.services.api_keys import (
    create_account,
    create_api_key,
    list_api_keys,
    revoke_api_key,
)

router = APIRouter()


class CreateAccountRequest(BaseModel):
    email: EmailStr


class CreateKeyRequest(BaseModel):
    label: str = Field(default="default", max_length=64)


class ApiKeyOut(BaseModel):
    id: str
    label: str
    key_preview: str
    created_at: str
    is_active: bool


class FullApiKeyOut(ApiKeyOut):
    key: str  # full key — shown ONCE at creation, never again


@router.post(
    "/account",
    status_code=201,
    summary="Create a new Datask account (email only, no credit card)",
)
async def register(body: CreateAccountRequest) -> JSONResponse:
    account = await create_account(email=body.email)
    return JSONResponse(status_code=201, content=account)


@router.post(
    "/keys",
    response_model=FullApiKeyOut,
    status_code=201,
    summary="Generate a new API key",
)
async def create_key(
    body: CreateKeyRequest,
    current_key=Depends(get_current_key),  # noqa: B008
) -> FullApiKeyOut:
    data = await create_api_key(
        account_id=current_key["account_id"],
        label=body.label,
    )
    return FullApiKeyOut(**data)


@router.get(
    "/keys",
    response_model=list[ApiKeyOut],
    summary="List all API keys for the authenticated account",
)
async def list_keys(current_key=Depends(get_current_key)) -> list[ApiKeyOut]:  # noqa: B008
    keys = await list_api_keys(account_id=current_key["account_id"])
    return [ApiKeyOut(**k) for k in keys]


@router.delete(
    "/keys/{key_id}",
    status_code=204,
    summary="Revoke an API key immediately",
)
async def revoke_key(
    key_id: str,
    current_key=Depends(get_current_key),  # noqa: B008
) -> None:
    await revoke_api_key(key_id=key_id, account_id=current_key["account_id"])
