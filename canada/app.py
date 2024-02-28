from __future__ import annotations

import os
import logging
from typing import Callable, TYPE_CHECKING

from aiohttp import web

from canada.api import entry, workbook, collection
from canada.app_stuff import attach_services, resolve_entity_aliases
from canada.settings import CanadaSettings
from canada.api.serializer import SimpleCanadaApiSerializer
import canada.api.collection.views
import canada.api.workbook.views
import canada.api.entry.views
import canada.api.lock.views
from canada.constants import EntityAliasMode
from canada.entity_alias_manager import DummyEntityAliasManager, InMemoryEntityAliasManager

from canada.yt_wb_manager.yt_client.yt_client import SimpleYtClient
from canada.yt_wb_manager.yt_client.auth import YTCookieAuthContext, YTNoAuthContext
from canada.yt_wb_manager.constants import YTAuthMode
from canada.yt_wb_manager.wb_manager import YTWorkbookManager
from canada.yt_wb_manager.serialization import SimpleCanadaStorageSerializer
from canada.yt_wb_manager import constants as yt_const

if TYPE_CHECKING:
    from canada.entity_alias_manager import BaseEntityAliasManager


def get_yt_cli_noauth_factory(settings: CanadaSettings):
    def yt_cli_factory(request: web.Request) -> SimpleYtClient:
        auth_context = YTNoAuthContext()
        return SimpleYtClient(yt_host=settings.YT_HOST, auth_context=auth_context, ca_file=settings.CA_FILE)

    return yt_cli_factory


def get_yt_cli_env_cookie_auth_factory(settings: CanadaSettings):
    def yt_cli_factory(request: web.Request) -> SimpleYtClient:
        auth_context = YTCookieAuthContext(
            cypress_cookie=os.environ["YT_COOKIE"],
            csrf_token=os.environ["YT_CSRF_TOKEN"]
        )
        return SimpleYtClient(yt_host=settings.YT_HOST, auth_context=auth_context, ca_file=settings.CA_FILE)

    return yt_cli_factory


def get_yt_cli_request_cookie_auth_factory(settings: CanadaSettings):
    def yt_cli_factory(request: web.Request) -> SimpleYtClient:
        auth_context = YTCookieAuthContext(
            cypress_cookie=request.cookies[yt_const.YT_COOKIE_TOKEN_NAME],
            csrf_token=request.headers[yt_const.YT_HEADER_CSRF_NAME]
        )
        return SimpleYtClient(yt_host=settings.YT_HOST, auth_context=auth_context, ca_file=settings.CA_FILE)

    return yt_cli_factory


def get_workbook_manager_factory(
        yt_cli_factory: Callable[[web.Request], SimpleYtClient],
        root_collection_node_id: str,
) -> Callable[[web.Request], YTWorkbookManager]:
    def workbook_manager_factory(request: web.Request) -> YTWorkbookManager:
        return YTWorkbookManager(
            yt_client=yt_cli_factory(request),
            root_collection_node_id=root_collection_node_id,
            serializer=SimpleCanadaStorageSerializer(root_collection_node_id=root_collection_node_id),
        )
    return workbook_manager_factory


def create_app(settings: CanadaSettings) -> web.Application:
    logging.basicConfig(level=logging.DEBUG)

    yt_cli_factory: Callable[[web.Request], SimpleYtClient]
    match settings.YT_AUTH_MODE:
        case YTAuthMode.disabled:
            yt_cli_factory = get_yt_cli_noauth_factory(settings)
        case YTAuthMode.cookie_from_env:
            yt_cli_factory = get_yt_cli_env_cookie_auth_factory(settings)
        case YTAuthMode.pass_request_creds:
            yt_cli_factory = get_yt_cli_request_cookie_auth_factory(settings)
        case _:
            raise ValueError(f"Unknown YTAuthMode: {settings.YT_AUTH_MODE}")

    entity_alias_manager: BaseEntityAliasManager
    match settings.ENTITY_ALIAS_MODE:
        case EntityAliasMode.disabled:
            entity_alias_manager = DummyEntityAliasManager()
        case EntityAliasMode.from_file:
            assert settings.ENTITY_ALIAS_CONFIG_PATH is not None
            entity_alias_manager = InMemoryEntityAliasManager.from_file(settings.ENTITY_ALIAS_CONFIG_PATH)
        case EntityAliasMode.from_env:
            entity_alias_manager = InMemoryEntityAliasManager.from_env()
        case _:
            raise ValueError(f"Unknown EntityAliasMode: {settings.ENTITY_ALIAS_MODE}")

    app_instance = web.Application(
        middlewares=[
            resolve_entity_aliases(entity_alias_manager=entity_alias_manager),
            attach_services(
                workbook_manager_factory=get_workbook_manager_factory(
                    yt_cli_factory=yt_cli_factory,
                    root_collection_node_id=settings.ROOT_COLLECTION_NODE_ID,
                ),
                api_serializer_factory=lambda: SimpleCanadaApiSerializer(entity_alias_manager=entity_alias_manager),
            ),
        ]
    )

    configure_routes(app_instance)

    return app_instance


async def gunicorn_app() -> web.Application:
    return create_app(settings=CanadaSettings.from_env())


def configure_routes(app_instance: web.Application):
    app_instance.add_routes(canada.api.entry.views.router)
    app_instance.add_routes(canada.api.workbook.views.router)
    app_instance.add_routes(canada.api.collection.views.router)
    app_instance.add_routes(canada.api.lock.views.router)


if __name__ == "__main__":
    app = create_app(settings=CanadaSettings.from_env())
    web.run_app(app, port=8888)
