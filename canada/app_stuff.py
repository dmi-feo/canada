import inspect
from dataclasses import dataclass

from aiohttp.web import middleware

from canada.yt_client import SimpleYtClient
from canada.wb_manager import WBManager
from canada import settings


@dataclass
class AppServices:
    wbman: WBManager


@middleware
async def attach_services(request, handler):
    app_services = AppServices(
        WBManager(yt_cli=SimpleYtClient(yt_host=settings.YT_HOST))
    )
    # FIXME: switch to class-based views without introspection
    handler_arg_names = inspect.signature(handler).parameters.keys()
    if "app_services" in handler_arg_names:
        resp = await handler(request, app_services=app_services)
    else:
        resp = await handler(request)

    return resp
