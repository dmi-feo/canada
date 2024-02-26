from contextlib import asynccontextmanager

import pytest
import aiohttp

from .common import EntityNotFound


# TODO: consider using it as a fixture or move to a lib
@asynccontextmanager
async def collection(client, title: str = "test_collection", parent_id: str | None = None):
    resp = await client.post(
        "/v1/collections",
        json={
            "title": title,
            "parentId": parent_id,
            "description": "",
        }
    )
    assert resp.status == 200
    data = await resp.json()
    coll_id = data["collectionId"]
    yield coll_id

    try:
        await delete_collection(client, collection_id=coll_id)
    except EntityNotFound:
        pass


async def delete_collection(client, collection_id: str):
    resp = await client.delete(f"/v1/collections/{collection_id}")
    if resp.status == 404:
        raise EntityNotFound()
    assert resp.status == 200


async def test_create_and_delete_collection(client, wb_manager):
    coll_title = "my_super_title_for_super_collection"
    async with collection(client, title=coll_title) as coll_id:
        coll_obj = await wb_manager.get_collection(coll_id)
        assert coll_obj.title == coll_title

    with pytest.raises(aiohttp.client_exceptions.ClientResponseError):  # FIXME: normal exceptions
        await wb_manager.get_collection(coll_id)
