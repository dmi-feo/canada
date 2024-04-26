from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import web

from canada.aiohttp_marshmallow.base import with_schema
from canada.api.common import schema
from canada.app_stuff import BaseView

if TYPE_CHECKING:
    from canada.types import JSON, JSONDict


router = web.RouteTableDef()


@router.view("/ping")
class PingView(BaseView):
    @with_schema(resp_schema=schema.PingResponse)
    async def get(self, data: JSONDict) -> JSON:
        """
        ping? pong!
        """
        return {"msg": "pong"}
