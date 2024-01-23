import functools
from typing import Type

import marshmallow as ma
from aiohttp import web


def response_schema(schema: Type[ma.Schema]):
    def wrapper(coro):
        @functools.wraps(coro)
        async def wrapped(*args, **kwargs):
            json_data = await coro(*args, **kwargs)
            resp = web.json_response(schema().dump(json_data))
            return resp
        return wrapped
    return wrapper


def request_schema(schema: Type[ma.Schema]):
    def wrapper(coro):
        @functools.wraps(coro)
        async def wrapped(request, *args, **kwargs):
            json_data = await request.json()
            ma_deser = schema().load(json_data)
            return await coro(request, *args, **kwargs, verified_json=ma_deser)
        return wrapped
    return wrapper
