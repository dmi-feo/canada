from __future__ import annotations

import inspect
from typing import Callable, Coroutine, Any, TYPE_CHECKING

import attr
from aiohttp.web import middleware

if TYPE_CHECKING:
    from canada.base_wb_manager import BaseWorkbookManager
    from canada.api.serializer import BaseCanadaApiSerializer
    from aiohttp.web import Request
    from canada.entity_alias_manager import BaseEntityAliasManager


@attr.s
class AppServices:
    wbman: BaseWorkbookManager = attr.ib()
    api_serializer: BaseCanadaApiSerializer = attr.ib()


def attach_services(
        workbook_manager_factory: Callable[[Request], BaseWorkbookManager],
        api_serializer_factory: Callable[[], BaseCanadaApiSerializer]
) -> Callable[[Any, Any], Coroutine[Any, Any, Any]]:
    @middleware
    async def attach_services_mw(request, handler):
        app_services = AppServices(
            wbman=workbook_manager_factory(request),
            api_serializer=api_serializer_factory(),
        )
        # FIXME: switch to class-based views in order to get rid of introspection
        handler_arg_names = inspect.signature(handler).parameters.keys()
        if "app_services" in handler_arg_names:
            resp = await handler(request, app_services=app_services)
        else:
            resp = await handler(request)

        return resp

    return attach_services_mw


def resolve_entity_aliases(entity_alias_manager: BaseEntityAliasManager):
    @middleware
    async def resolve_entity_aliases_mw(request, handler):
        for key in ("entry_id", "workbook_id", "collection_id"):
            if key in request.match_info:
                request.match_info[key] = entity_alias_manager.resolve_alias(request.match_info[key])
            if key in request.query:
                request.query[key] = entity_alias_manager.resolve_alias(request.query[key])

        resp = await handler(request)
        return resp

    return resolve_entity_aliases_mw
