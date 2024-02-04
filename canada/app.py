import logging

from aiohttp import web

from canada.api import entry, workbook, collection
from canada.app_stuff import attach_services
import canada.api.collection.views
import canada.api.workbook.views
import canada.api.entry.views


logging.basicConfig(level=logging.DEBUG)
app = web.Application(
    middlewares=[
        attach_services,
    ]
)

app.add_routes(canada.api.entry.views.router)
app.add_routes(canada.api.workbook.views.router)
app.add_routes(canada.api.collection.views.router)


if __name__ == "__main__":
    web.run_app(app, port=8888)
