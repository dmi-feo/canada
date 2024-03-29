import pytest


async def test_create_and_delete_collection(wb_client):
    coll_title = "my_super_title_for_super_collection"
    async with wb_client.collection_ctx(title=coll_title) as coll_id:
        collection = await wb_client.get_collection(coll_id)
        assert collection["title"] == coll_title

    with pytest.raises(Exception):  # FIXME: normal exceptions
        await wb_client.get_collection(coll_id)


async def test_create_nested_collections(wb_client):
    async with wb_client.collection_ctx(title="coll1") as coll1_id:
        async with wb_client.collection_ctx(title="coll2", parent_id=coll1_id) as coll2_id:
            collection_2 = await wb_client.get_collection(coll2_id)
            assert collection_2["parentId"] == coll1_id


async def test_get_nonexistent_collection(wb_client):
    resp = await wb_client.client.get("/v1/collections/1-238c-1012f-1f9b37b")
    assert resp.status == 424
    assert "Error resolving path #1-238c-1012f-1f9b37b" in await resp.text()
