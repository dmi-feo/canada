from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
)

import aiohttp.web
from aiohttp.web import (
    View,
    middleware,
)
import attr

from canada.base_wb_manager.exc import WBManagerStorageError
from canada.constants import REQUEST_KEY_APP_SERVICES
from canada.factories import WorkbookManagerFactory


if TYPE_CHECKING:
    from aiohttp.typedefs import Handler
    from aiohttp.web import (
        Request,
        StreamResponse,
    )

    from canada.api.serializer import BaseCanadaApiSerializer
    from canada.base_wb_manager.base_wb_manager import BaseWorkbookManager


class BaseView(View):
    def __init__(self, request: Request) -> None:
        super().__init__(request)
        self.app_services: AppServices = request[REQUEST_KEY_APP_SERVICES]


@attr.s
class AppServices:
    wbman: BaseWorkbookManager = attr.ib()
    api_serializer: BaseCanadaApiSerializer = attr.ib()


def attach_services(
    workbook_manager_factory: WorkbookManagerFactory,
    api_serializer_factory: Callable[[], BaseCanadaApiSerializer],
) -> Callable[[Request, Handler], Awaitable[StreamResponse]]:
    @middleware
    async def attach_services_mw(request: Request, handler: Handler) -> StreamResponse:
        workbook_manager = await workbook_manager_factory.make_workbook_manager(request)
        app_services = AppServices(
            wbman=workbook_manager,
            api_serializer=api_serializer_factory(),
        )

        request[REQUEST_KEY_APP_SERVICES] = app_services
        resp = await handler(request)
        return resp

    return attach_services_mw


@middleware
async def error_handling(request: Request, handler: Handler) -> StreamResponse:
    # TODO: make compatible with United Storage
    try:
        return await handler(request)
    except WBManagerStorageError as err:
        raise aiohttp.web.HTTPFailedDependency(text=err.message)
