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

    resp = await handler(request, app_services=app_services)
    return resp
