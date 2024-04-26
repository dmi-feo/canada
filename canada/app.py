from __future__ import annotations

import logging
import ssl

from aiohttp import web

import canada.api.collection.views
import canada.api.common.views
import canada.api.entry.views
import canada.api.lock.views
import canada.api.workbook.views
from canada.api.serializer import SimpleCanadaApiSerializer
from canada.app_stuff import attach_services, error_handling
from canada.factories import (BaseYTCliFactory, WorkbookManagerFactory, YtCliEnvCookieAuthFactory, YtCliNoauthFactory,
                              YtCliRequestCookieAuthFactory)
from canada.settings import CanadaSettings
from canada.yt_wb_manager.constants import YTAuthMode


def create_app(settings: CanadaSettings) -> web.Application:
    logging.basicConfig(level=logging.DEBUG)

    ssl_context = ssl.create_default_context(cafile=settings.CA_FILE)

    yt_cli_factory: BaseYTCliFactory
    match settings.YT_AUTH_MODE:
        case YTAuthMode.disabled:
            yt_cli_factory = YtCliNoauthFactory(
                yt_host=settings.YT_HOST,
                ssl_context=ssl_context,
            )
        case YTAuthMode.cookie_from_env:
            yt_cli_factory = YtCliEnvCookieAuthFactory(
                yt_host=settings.YT_HOST,
                ssl_context=ssl_context,
            )
        case YTAuthMode.pass_request_creds:
            yt_cli_factory = YtCliRequestCookieAuthFactory(
                yt_host=settings.YT_HOST,
                ssl_context=ssl_context,
            )
        case _:
            raise ValueError(f"Unknown YTAuthMode: {settings.YT_AUTH_MODE}")

    app_instance = web.Application(
        middlewares=[
            error_handling,
            attach_services(
                workbook_manager_factory=WorkbookManagerFactory(
                    yt_cli_factory=yt_cli_factory,
                    root_collection_node_id=settings.ROOT_COLLECTION_NODE_ID,
                ),
                api_serializer_factory=lambda: SimpleCanadaApiSerializer(),
            ),
        ]
    )

    configure_routes(app_instance)

    return app_instance


async def gunicorn_app() -> web.Application:
    return create_app(settings=CanadaSettings.from_env())


def configure_routes(app_instance: web.Application) -> None:
    app_instance.add_routes(canada.api.entry.views.router)
    app_instance.add_routes(canada.api.workbook.views.router)
    app_instance.add_routes(canada.api.collection.views.router)
    app_instance.add_routes(canada.api.lock.views.router)
    app_instance.add_routes(canada.api.common.views.router)


if __name__ == "__main__":
    app = create_app(settings=CanadaSettings.from_env())
    web.run_app(app, port=8888)
