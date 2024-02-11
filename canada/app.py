import logging

from aiohttp import web

from canada.api import entry, workbook, collection
from canada.app_stuff import attach_services
import canada.api.collection.views
import canada.api.workbook.views
import canada.api.entry.views

from canada.yt_client import SimpleYtClient
from canada import settings


def create_app() -> web.Application:
    logging.basicConfig(level=logging.DEBUG)
    app_instance = web.Application(
        middlewares=[
            attach_services(
                yt_cli_factory=lambda: SimpleYtClient(yt_host=settings.YT_HOST),
                root_collection_node_id=settings.ROOT_COLLECTION_NODE_ID,
            ),
        ]
    )

    configure_routes(app_instance)

    return app_instance


def configure_routes(app_instance: web.Application):
    app_instance.add_routes(canada.api.entry.views.router)
    app_instance.add_routes(canada.api.workbook.views.router)
    app_instance.add_routes(canada.api.collection.views.router)


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, port=8888)
