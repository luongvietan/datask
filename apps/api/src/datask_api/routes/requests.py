# -*- coding: utf-8 -*-
"""Request log routes — paginated recent requests for dashboard."""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from datask_api.db.repositories import usage as usage_repo
from datask_api.db.session import get_session_factory
from datask_api.middleware.auth import get_current_key

router = APIRouter()


@router.get(
    "/requests",
    summary="List recent requests (paginated, account-scoped)",
)
async def list_requests(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    layer: int | None = Query(None, ge=1, le=3),
    success: bool | None = None,
    current_key=Depends(get_current_key),  # noqa: B008
) -> JSONResponse:
    factory = get_session_factory()
    async with factory() as session:
        result = await usage_repo.list_requests(
            session,
            account_id=current_key["account_id"],
            limit=limit,
            offset=offset,
            layer=layer,
            success=success,
        )
    return JSONResponse(content=result)
