from __future__ import annotations
import functools
from typing import Type, Awaitable, Callable, TypeVar, TypeAlias

import marshmallow as ma
from aiohttp import web
from aiohttp.web_response import Response

from canada.app_stuff import BaseView
from canada.types import JSON, JSONDict


ViewType = TypeVar("ViewType", bound=BaseView)

View: TypeAlias = Callable[[ViewType], Awaitable[Response]]
ViewExpectingData: TypeAlias = Callable[[ViewType, JSONDict], Awaitable[JSON]]


def with_schema(
        req_schema: Type[ma.Schema] | None = None,
        resp_schema: Type[ma.Schema] = ma.Schema
) -> Callable[[ViewExpectingData[ViewType]], View[ViewType]]:
    def wrapper(coro: ViewExpectingData[ViewType]) -> View[ViewType]:
        @functools.wraps(coro)
        async def wrapped(view_instance: ViewType) -> web.Response:
            if req_schema is not None:
                incoming_json_data = await view_instance.request.json()
                ma_deser = req_schema().load(incoming_json_data)
            else:
                ma_deser = {}
            out_data = await coro(view_instance, ma_deser)
            resp = web.json_response(resp_schema().dump(out_data))
            return resp

        return wrapped

    return wrapper
