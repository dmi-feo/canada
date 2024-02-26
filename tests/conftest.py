import pytest

from canada.app import create_app
from canada.settings import CanadaSettings
from canada.yt_wb_manager.yt_client.yt_client import SimpleYtClient
from canada.yt_wb_manager.yt_client.auth import YTNoAuthContext
from canada.yt_wb_manager.wb_manager import YTWorkbookManager
from canada.yt_wb_manager.serialization import SimpleCanadaStorageSerializer


@pytest.fixture(scope="function")
def app_settings():
    return CanadaSettings.from_env()


@pytest.fixture(scope="function")
async def client(aiohttp_client, app_settings):
    app = create_app(settings=app_settings)
    return await aiohttp_client(app)


@pytest.fixture(scope="function")
def yt_client(app_settings):
    return SimpleYtClient(yt_host=app_settings.YT_HOST, auth_context=YTNoAuthContext())


@pytest.fixture(scope="function")
def wb_manager(yt_client, app_settings):
    return YTWorkbookManager(
        yt_client=yt_client,
        root_collection_node_id=app_settings.ROOT_COLLECTION_NODE_ID,
        serializer=SimpleCanadaStorageSerializer(root_collection_node_id=app_settings.ROOT_COLLECTION_NODE_ID),
    )
