from __future__ import annotations
import typing

from aiohttp import web

from canada.aiohttp_marshmallow.base import request_schema, response_schema
from canada.api.workbook import schema

if typing.TYPE_CHECKING:
    from canada.app_stuff import AppServices


router = web.RouteTableDef()


@router.post("/v2/workbooks")
@request_schema(schema.CreateWorkbookRequest)
@response_schema(schema.CreateWorkbookResponse)
async def create_workbook(request, verified_json: dict, app_services: AppServices):
    workbook = app_services.api_serializer.deserialize_workbook(verified_json)
    workbook_id = await app_services.wbman.create_workbook(workbook)
    workbook = await app_services.wbman.get_workbook(workbook_id)
    return app_services.api_serializer.serialize_workbook(workbook)


@router.get('/v2/workbooks/{workbook_id}')
@response_schema(schema.GetWorkbookResponse)
async def get_workbook(request, app_services: AppServices):
    workbook_id = request.match_info["workbook_id"]
    workbook = await app_services.wbman.get_workbook(workbook_id)
    return app_services.api_serializer.serialize_workbook(workbook)


@router.get("/v2/workbooks/{workbook_id}/entries")
@response_schema(schema.GetWorkbookEntriesResponse)
async def get_workbook_entries(request, app_services: AppServices):
    workbook_id = request.match_info["workbook_id"]
    entries = await app_services.wbman.get_workbook_entries(workbook_id)
    return {"entries": [app_services.api_serializer.serialize_entry(entry) for entry in entries]}
