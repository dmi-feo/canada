from __future__ import annotations

from typing import Callable, TYPE_CHECKING, Awaitable

import attr
from aiohttp.web import middleware, View

from canada.constants import REQUEST_KEY_APP_SERVICES

if TYPE_CHECKING:
    from canada.base_wb_manager import BaseWorkbookManager
    from canada.api.serializer import BaseCanadaApiSerializer
    from aiohttp.web import Request, StreamResponse
    from aiohttp.typedefs import Handler


class BaseView(View):
    def __init__(self, request: Request) -> None:
        super().__init__(request)
        self.app_services: AppServices = request[REQUEST_KEY_APP_SERVICES]


@attr.s
class AppServices:
    wbman: BaseWorkbookManager = attr.ib()
    api_serializer: BaseCanadaApiSerializer = attr.ib()


def attach_services(
        workbook_manager_factory: Callable[[Request], BaseWorkbookManager],
        api_serializer_factory: Callable[[], BaseCanadaApiSerializer]
) -> Callable[[Request, Handler], Awaitable[StreamResponse]]:
    @middleware
    async def attach_services_mw(request: Request, handler: Handler) -> StreamResponse:
        app_services = AppServices(
            wbman=workbook_manager_factory(request),
            api_serializer=api_serializer_factory(),
        )

        request[REQUEST_KEY_APP_SERVICES] = app_services
        resp = await handler(request)
        return resp

    return attach_services_mw
