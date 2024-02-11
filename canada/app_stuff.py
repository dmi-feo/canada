import inspect
from dataclasses import dataclass
from typing import Callable, Coroutine, Any

from aiohttp.web import middleware

from canada.wb_manager import WBManager


@dataclass
class AppServices:
    wbman: WBManager


def attach_services(yt_cli_factory: Callable) -> Callable[[Any, Any], Coroutine[Any, Any, Any]]:
    @middleware
    async def attach_services_mw(request, handler):
        app_services = AppServices(
            WBManager(yt_cli=yt_cli_factory())
        )
        # FIXME: switch to class-based views without introspection
        handler_arg_names = inspect.signature(handler).parameters.keys()
        if "app_services" in handler_arg_names:
            resp = await handler(request, app_services=app_services)
        else:
            resp = await handler(request)

        return resp

    return attach_services_mw
