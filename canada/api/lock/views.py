from __future__ import annotations
import typing

from aiohttp import web

from canada.aiohttp_marshmallow.base import response_schema, request_schema
from canada.api.lock import schema

if typing.TYPE_CHECKING:
    from canada.app_stuff import AppServices


router = web.RouteTableDef()


@router.post("/v1/locks/{entry_id}")
@request_schema(schema.CreateLockRequest)
@response_schema(schema.CreateLockResponse)
async def create_lock(request: web.Request, verified_json: dict, app_services: AppServices):
    entry_id = request.match_info["entry_id"]
    lock_id = await app_services.wbman.set_lock(
        entry_id, duration=verified_json.get("duration"), force=verified_json.get("force")
    )
    return {"lockToken": lock_id}


@router.delete("/v1/locks/{entry_id}")
@response_schema(schema.DeleteLockResponse)
async def delete_lock(request: web.Request, app_services: AppServices):
    entry_id = request.match_info["entry_id"]
    lock_token = request.query["lockToken"]
    await app_services.wbman.delete_lock(entry_id, lock_token)
    return {}
