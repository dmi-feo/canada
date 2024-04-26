from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import web

from canada.aiohttp_marshmallow.base import with_schema
from canada.api.lock import schema
from canada.app_stuff import BaseView


if TYPE_CHECKING:
    from canada.types import (
        JSON,
        JSONDict,
    )


router = web.RouteTableDef()


@router.view("/v1/locks/{entry_id}")
class LockView(BaseView):
    @with_schema(req_schema=schema.CreateLockRequest, resp_schema=schema.CreateLockResponse)
    async def post(self, data: JSONDict) -> JSON:
        """
        Create lock for entry
        """
        entry_id = self.request.match_info["entry_id"]

        duration = data.get("duration")
        if duration is not None:
            assert isinstance(duration, int)

        force = data.get("force")
        if force is not None:
            assert isinstance(force, bool)

        lock_id = await self.app_services.wbman.set_lock(entry_id, duration=duration, force=force)
        return {"lockToken": lock_id}

    @with_schema(resp_schema=schema.DeleteLockResponse)
    async def delete(self, data: JSONDict) -> JSON:
        """
        Delete lock for entry
        """
        entry_id = self.request.match_info["entry_id"]
        lock_token = self.request.query["lockToken"]
        await self.app_services.wbman.delete_lock(entry_id, lock_token)
        return {}
