from __future__ import annotations

import inspect
from typing import Callable, Coroutine, Any, TYPE_CHECKING

import attr
from aiohttp.web import middleware

from canada.api.serializer import SimpleCanadaApiSerializer

if TYPE_CHECKING:
    from canada.wb_manager.wb_manager import BaseWorkbookManager
    from canada.api.serializer import BaseCanadaApiSerializer
    from aiohttp.web import Request


@attr.s
class AppServices:
    wbman: BaseWorkbookManager = attr.ib()
    api_serializer: BaseCanadaApiSerializer = attr.ib()


def attach_services(
        workbook_manager_factory: Callable[[Request], BaseWorkbookManager]
) -> Callable[[Any, Any], Coroutine[Any, Any, Any]]:
    @middleware
    async def attach_services_mw(request, handler):
        app_services = AppServices(
            wbman=workbook_manager_factory(request),
            api_serializer=SimpleCanadaApiSerializer(),
        )
        # FIXME: switch to class-based views in order to get rid of introspection
        handler_arg_names = inspect.signature(handler).parameters.keys()
        if "app_services" in handler_arg_names:
            resp = await handler(request, app_services=app_services)
        else:
            resp = await handler(request)

        return resp

    return attach_services_mw
