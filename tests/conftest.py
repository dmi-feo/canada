import pathlib

import pytest

from canada.app import create_app
from canada.settings import CanadaSettings
from canada.constants import EntityAliasMode

from .common import WBTestClient


@pytest.fixture(scope="function")
def app_settings():
    settings = CanadaSettings.from_env()
    settings.ENTITY_ALIAS_MODE = EntityAliasMode.from_file
    settings.ENTITY_ALIAS_CONFIG_PATH = pathlib.Path(__file__).parent.joinpath("aliases.json").resolve()
    return settings


@pytest.fixture(scope="function")
async def client(aiohttp_client, app_settings):
    app = create_app(settings=app_settings)
    return await aiohttp_client(app)


@pytest.fixture(scope="function")
def wb_client(client):
    return WBTestClient(client=client)
