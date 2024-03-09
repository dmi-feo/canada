from __future__ import annotations
from typing import TYPE_CHECKING

from aiohttp import web

from canada.aiohttp_marshmallow.base import handler_with_schema
from canada.api.workbook import schema
from canada.app_stuff import BaseView

if TYPE_CHECKING:
    from canada.types import JSON, JSONDict


router = web.RouteTableDef()


@router.view("/v2/workbooks")
class WorkbooksView(BaseView):
    @handler_with_schema(req_schema=schema.CreateWorkbookRequest, resp_schema=schema.CreateWorkbookResponse)
    async def post(self, data: JSONDict) -> JSON:
        """
        Create workbook
        """
        workbook = self.app_services.api_serializer.deserialize_workbook(data)
        workbook_id = await self.app_services.wbman.create_workbook(workbook)
        workbook = await self.app_services.wbman.get_workbook(workbook_id)
        return self.app_services.api_serializer.serialize_workbook(workbook)


@router.view("/v2/workbooks/{workbook_id}")
class WorkbookItemView(BaseView):
    @handler_with_schema(resp_schema=schema.GetWorkbookResponse)
    async def get(self, data: JSONDict) -> JSON:
        """
        Get workbook info
        """
        workbook_id = self.request.match_info["workbook_id"]
        workbook = await self.app_services.wbman.get_workbook(workbook_id)
        return self.app_services.api_serializer.serialize_workbook(workbook)

    @handler_with_schema(resp_schema=schema.DeleteWorkbookResponse)
    async def delete(self, data: JSONDict) -> JSON:
        """
        Delete workbook
        """
        workbook_id = self.request.match_info["workbook_id"]
        await self.app_services.wbman.delete_workbook(workbook_id)
        return {}


@router.view("/v2/workbooks/{workbook_id}/entries")
class WorkbookEntriesView(BaseView):
    @handler_with_schema(resp_schema=schema.GetWorkbookEntriesResponse)
    async def get(self, data: JSON) -> JSON:
        """
        Get workbook entries
        """
        workbook_id = self.request.match_info["workbook_id"]
        scope = self.request.query.get("scope")
        entries = await self.app_services.wbman.get_workbook_entries(workbook_id, scope=scope)
        return {"entries": [self.app_services.api_serializer.serialize_entry(entry) for entry in entries]}
