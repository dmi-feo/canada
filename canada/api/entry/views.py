from __future__ import annotations
import typing

from aiohttp import web

from canada.aiohttp_marshmallow.base import response_schema, request_schema
from canada.api.entry import schema

if typing.TYPE_CHECKING:
    from canada.app_stuff import AppServices


router = web.RouteTableDef()


@router.get('/v1/entries/{entry_id}')
@router.get('/private/entries/{entry_id}')
@response_schema(schema.GetEntryResponse)
async def get_entry(request, app_services: AppServices):
    entry_id = request.match_info["entry_id"]
    entry = await app_services.wbman.get_entry(entry_id)

    return app_services.api_serializer.serialize_entry(entry)


@router.post("/v1/entries")
@router.post("/private/entries")
@request_schema(schema.CreateEntryRequest)
@response_schema(schema.CreateEntryResponse)
async def create_entry(request, verified_json: dict, app_services: AppServices):
    entry = app_services.api_serializer.deserialize_entry(verified_json)
    entry_id = await app_services.wbman.create_entry(entry)

    return {"entryId": entry_id}


@router.post("/v1/entries/{entry_id}")
@request_schema(schema.UpdateEntryRequest)
@response_schema(schema.UpdateEntryResponse)
async def update_entry(request, verified_json: dict, app_services: AppServices):
    entry_id = request.match_info["entry_id"]
    await app_services.wbman.update_entry(
        entry_id=entry_id,
        entry_data=verified_json.get("data"),
        unversioned_data=verified_json.get("unversionedData"),
        lock_token=verified_json.get("lockToken"),
    )

    return {"entryId": entry_id}


@router.get("/v1/entries/{entry_id}/meta")
@response_schema(schema.GetEntryMetaResponse)
async def get_entry_meta(request, app_services: AppServices):
    return {}


@router.delete("/v1/entries/{entry_id}")
@response_schema(schema.DeleteEntryResponse)
async def delete_entry(request, app_services: AppServices):
    entry_id = request.match_info["entry_id"]
    await app_services.wbman.delete_entry(entry_id)
