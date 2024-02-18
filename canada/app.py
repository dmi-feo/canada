import os
import logging
from typing import Callable

from aiohttp import web

from canada.api import entry, workbook, collection
from canada.app_stuff import attach_services
import canada.api.collection.views
import canada.api.workbook.views
import canada.api.entry.views
from canada import constants

from canada.yt_client import SimpleYtClient, YTCookieAuthContext, YTNoAuthContext
from canada.settings import CanadaSettings, YTAuthMode


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
            cypress_cookie=request.cookies[constants.YT_COOKIE_TOKEN_NAME],
            csrf_token=request.headers[constants.YT_HEADER_CSRF_NAME]
        )
        return SimpleYtClient(yt_host=settings.YT_HOST, auth_context=auth_context, ca_file=settings.CA_FILE)

    return yt_cli_factory


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

    app_instance = web.Application(
        middlewares=[
            attach_services(
                yt_cli_factory=yt_cli_factory,
                root_collection_node_id=settings.ROOT_COLLECTION_NODE_ID,
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


if __name__ == "__main__":
    app = create_app(settings=CanadaSettings.from_env())
    web.run_app(app, port=8888)
