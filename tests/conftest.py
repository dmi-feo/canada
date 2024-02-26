import pytest

from canada.app import create_app
from canada.settings import CanadaSettings

from .common import WBTestClient


@pytest.fixture(scope="function")
def app_settings():
    return CanadaSettings.from_env()


@pytest.fixture(scope="function")
async def client(aiohttp_client, app_settings):
    app = create_app(settings=app_settings)
    return await aiohttp_client(app)


@pytest.fixture(scope="function")
def wb_client(client):
    return WBTestClient(client=client)
