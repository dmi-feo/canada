from aiohttp import web

from canada.app_stuff import AppServices
from canada.aiohttp_marshmallow.base import response_schema, request_schema
from canada.api.entry import schema


router = web.RouteTableDef()


@router.get('/v1/entries/{entry_id}')
@router.get('/private/entries/{entry_id}')
@response_schema(schema.GetEntryResponse)
async def get_entry(request, app_services: AppServices):
    entry_id = request.match_info["entry_id"]
    entry = await app_services.wbman.get_entry(entry_id)

    return entry


@router.post("/v1/entries")
@router.post("/private/entries")
@request_schema(schema.CreateEntryRequest)
@response_schema(schema.CreateEntryResponse)
async def create_entry(request, verified_json: dict, app_services: AppServices):
    entry_id = await app_services.wbman.create_entry(
        name=verified_json["name"],
        workbook_id=verified_json["workbook_id"],
        entry_data=verified_json["data"],
        unversioned_data=verified_json["unversioned_data"],
        scope=verified_json["scope"],
        entry_type=verified_json["type"],
    )

    return {"entry_id": entry_id}


@router.post("/v1/entries/{entry_id}")
@request_schema(schema.UpdateEntryRequest)
@response_schema(schema.UpdateEntryResponse)
async def update_entry(request, verified_json: dict, app_services: AppServices):
    entry_id = request.match_info["entry_id"]
    await app_services.wbman.update_entry(
        entry_id=entry_id,
        entry_data=verified_json["data"],
        unversioned_data=verified_json["unversioned_data"],
    )

    return {"entry_id": entry_id}
