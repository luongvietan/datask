# -*- coding: utf-8 -*-
"""
Webhook endpoint CRUD — /v1/webhooks
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

from datask_api.middleware.auth import get_current_key
from datask_api.services.webhooks import (
    create_webhook,
    delete_webhook,
    list_webhooks,
)

router = APIRouter()


class CreateWebhookRequest(BaseModel):
    url: str  # Sử dụng str thay vì HttpUrl để dễ serialize
    events: str = "*"


@router.get(
    "/webhooks",
    summary="List webhook endpoints",
)
async def list_endpoints(
    current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    endpoints = await list_webhooks(current_key["account_id"])
    return JSONResponse(content=endpoints)


@router.post(
    "/webhooks",
    status_code=201,
    summary="Register a new webhook endpoint",
)
async def create_endpoint(
    body: CreateWebhookRequest,
    current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    endpoint = await create_webhook(
        account_id=current_key["account_id"],
        url=str(body.url),
        events=body.events,
    )
    return JSONResponse(status_code=201, content=endpoint)


@router.delete(
    "/webhooks/{webhook_id}",
    status_code=204,
    summary="Delete a webhook endpoint",
)
async def delete_endpoint(
    webhook_id: str,
    current_key=Depends(get_current_key),  # noqa: B008
) -> None:
    await delete_webhook(webhook_id=webhook_id, account_id=current_key["account_id"])
