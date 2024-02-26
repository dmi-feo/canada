from contextlib import asynccontextmanager


class EntityNotFound(Exception):
    pass


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


@asynccontextmanager
async def workbook(client, title: str = "test_workbook", collection_id: str | None = None):
    resp = await client.post(
        "/v2/workbooks",
        json={
            "title": title,
            "collectionId": collection_id,
            "description": "",
        }
    )
    assert resp.status == 200
    data = await resp.json()
    wb_id = data["workbookId"]
    yield wb_id

    try:
        await delete_workbook(client, workbook_id=wb_id)
    except EntityNotFound:
        pass


async def delete_workbook(client, workbook_id: str):
    resp = await client.delete(f"/v2/workbooks/{workbook_id}")
    if resp.status == 404:
        raise EntityNotFound()
    assert resp.status == 200
