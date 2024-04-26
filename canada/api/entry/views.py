from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import web

from canada.aiohttp_marshmallow.base import with_schema
from canada.api.entry import schema
from canada.app_stuff import BaseView


if TYPE_CHECKING:
    from canada.types import (
        JSON,
        JSONDict,
    )


router = web.RouteTableDef()


@router.view("/v1/entries/{entry_id}")
@router.view("/private/entries/{entry_id}")
class EntryItemView(BaseView):
    @with_schema(resp_schema=schema.GetEntryResponse)
    async def get(self, data: JSONDict) -> JSON:
        """
        Get entry
        """
        entry_id = self.request.match_info["entry_id"]
        entry = await self.app_services.wbman.get_entry(entry_id)

        return self.app_services.api_serializer.serialize_entry(entry)

    @with_schema(req_schema=schema.UpdateEntryRequest, resp_schema=schema.UpdateEntryResponse)
    async def post(self, data: JSONDict) -> JSON:
        """
        Update entry
        """
        entry_id = self.request.match_info["entry_id"]

        lock_token = data.get("lockToken")
        if lock_token is not None:
            assert isinstance(lock_token, str)

        entry_data, unversioned_data = data.get("data"), data.get("unversionedData")
        assert isinstance(entry_data, dict) or entry_data is None
        assert isinstance(unversioned_data, dict) or unversioned_data is None

        await self.app_services.wbman.update_entry(
            entry_id=entry_id,
            entry_data=entry_data,
            unversioned_data=unversioned_data,
            lock_token=lock_token,
        )

        return {"entryId": entry_id}

    @with_schema(resp_schema=schema.DeleteEntryResponse)
    async def delete(self, data: JSONDict) -> JSON:
        """
        Delete entry
        """
        entry_id = self.request.match_info["entry_id"]
        await self.app_services.wbman.delete_entry(entry_id)
        return {}


@router.view("/v1/entries")
@router.view("/private/entries")
class EntriesView(BaseView):
    @with_schema(req_schema=schema.CreateEntryRequest, resp_schema=schema.CreateEntryResponse)
    async def post(self, data: JSONDict) -> JSON:
        """
        Create entry
        """
        entry = self.app_services.api_serializer.deserialize_entry(data)
        entry_id = await self.app_services.wbman.create_entry(entry)

        return {"entryId": entry_id}


@router.view("/v1/entries/{entry_id}/meta")
class EntryMetaView(BaseView):
    @with_schema(resp_schema=schema.GetEntryMetaResponse)
    async def get(self, data: JSONDict) -> JSON:
        """
        Get entry meta
        """
        return {}
