from aiohttp import web

from canada.yt_client import get_yt_cli
from canada.settings import YT_HOME_PREFIX
from canada.app_stuff import AppServices
from canada.aiohttp_marshmallow.base import request_schema, response_schema
from canada.api.workbook import schema
from canada.id import ID


router = web.RouteTableDef()


@router.post("/v2/workbooks")
@request_schema(schema.CreateWorkbookRequest)
@response_schema(schema.CreateWorkbookResponse)
async def create_workbook(request, verified_json: dict, app_services: AppServices):
    workbook_id = await app_services.wbman.create_workbook(
        title=verified_json["title"],
        collection_id=ID.from_str(verified_json["collectionId"]),
        description=verified_json["description"],
    )
    data = await app_services.wbman.get_workbook(workbook_id)
    return data


@router.get('/v2/workbooks/{workbook_id}')
@response_schema(schema.GetWorkbookResponse)
async def get_workbook(request, app_services: AppServices):
    workbook_id = ID.from_str(request.match_info["workbook_id"])
    data = await app_services.wbman.get_workbook(workbook_id)
    return data


@router.get("/v2/workbooks/{workbook_id}/entries")
@response_schema(schema.GetWorkbookEntriesResponse)
async def get_workbook_entries(request, app_services: AppServices):
    workbook_id = ID.from_str(request.match_info["workbook_id"])
    data = await app_services.wbman.get_workbook_entries(workbook_id)
    return {"entries": data}
