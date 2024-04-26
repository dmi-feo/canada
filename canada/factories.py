from __future__ import annotations

import abc
import os
import ssl

import attr
from aiohttp import web

from canada.yt_wb_manager import constants as yt_const
from canada.yt_wb_manager.serialization import SimpleCanadaStorageSerializer
from canada.yt_wb_manager.wb_manager import YTWorkbookManager, WBAwareYtClient
from canada.yt_wb_manager.yt_client.auth import YTNoAuthContext, YTCookieAuthContext


class BaseYTCliFactory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def make_yt_client(self, request: web.Request) -> WBAwareYtClient:
        pass


@attr.s
class YtCliNoauthFactory(BaseYTCliFactory):
    _yt_host: str = attr.ib()
    _ssl_context: ssl.SSLContext = attr.ib()

    async def make_yt_client(self, request: web.Request) -> WBAwareYtClient:
        auth_context = YTNoAuthContext()
        return WBAwareYtClient(
            yt_host=self._yt_host,
            auth_context=auth_context,
            ssl_context=self._ssl_context,
        )


@attr.s
class YtCliEnvCookieAuthFactory(BaseYTCliFactory):
    _yt_host: str = attr.ib()
    _ssl_context: ssl.SSLContext = attr.ib()

    async def make_yt_client(self, request: web.Request) -> WBAwareYtClient:
        client_without_csrf = WBAwareYtClient(
            yt_host=self._yt_host,
            auth_context=YTCookieAuthContext(
                cypress_cookie=os.environ["YT_COOKIE"],
            ),
            ssl_context=self._ssl_context,
        )
        csrf_token = await client_without_csrf.get_csrf_token()
        return WBAwareYtClient(
            yt_host=self._yt_host,
            auth_context=YTCookieAuthContext(
                cypress_cookie=os.environ["YT_COOKIE"],
                csrf_token=csrf_token,
            ),
            ssl_context=self._ssl_context,
        )


@attr.s
class YtCliRequestCookieAuthFactory(BaseYTCliFactory):
    _yt_host: str = attr.ib()
    _ssl_context: ssl.SSLContext = attr.ib()

    async def make_yt_client(self, request: web.Request) -> WBAwareYtClient:
        client_without_csrf = WBAwareYtClient(
            yt_host=self._yt_host,
            auth_context=YTCookieAuthContext(
                cypress_cookie=request.cookies[yt_const.YT_COOKIE_TOKEN_NAME],
            ),
            ssl_context=self._ssl_context,
        )
        csrf_token = await client_without_csrf.get_csrf_token()
        return WBAwareYtClient(
            yt_host=self._yt_host,
            auth_context=YTCookieAuthContext(
                cypress_cookie=request.cookies[yt_const.YT_COOKIE_TOKEN_NAME],
                csrf_token=csrf_token,
            ),
            ssl_context=self._ssl_context,
        )


@attr.s
class WorkbookManagerFactory:
    _yt_cli_factory: BaseYTCliFactory = attr.ib()
    _root_collection_node_id: str = attr.ib()

    async def make_workbook_manager(self, request: web.Request) -> YTWorkbookManager:
        yt_client = await self._yt_cli_factory.make_yt_client(request)
        return YTWorkbookManager(
            yt_client=yt_client,
            root_collection_node_id=self._root_collection_node_id,
            serializer=SimpleCanadaStorageSerializer(root_collection_node_id=self._root_collection_node_id),
        )
