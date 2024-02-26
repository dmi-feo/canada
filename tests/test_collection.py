import pytest
import aiohttp

from .common import collection


async def test_create_and_delete_collection(client, wb_manager):
    coll_title = "my_super_title_for_super_collection"
    async with collection(client, title=coll_title) as coll_id:
        coll_obj = await wb_manager.get_collection(coll_id)
        assert coll_obj.title == coll_title

    with pytest.raises(aiohttp.client_exceptions.ClientResponseError):  # FIXME: normal exceptions
        await wb_manager.get_collection(coll_id)


async def test_create_nested_collections(client, wb_manager):
    async with collection(client, title="coll1") as coll1_id:
        async with collection(client, title="coll2", parent_id=coll1_id) as coll2_id:
            coll2_obj = await wb_manager.get_collection(coll2_id)
            assert coll2_obj.parent_id == coll1_id
