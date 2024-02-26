from contextlib import asynccontextmanager

import pytest
import aiohttp

from .common import EntityNotFound


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


async def test_create_and_delete_workbook(client, wb_manager):
    wb_title = "my_super_title_for_super_workbook"
    async with workbook(client, title=wb_title) as wb_id:
        wb_obj = await wb_manager.get_workbook(wb_id)
        assert wb_obj.title == wb_title

    with pytest.raises(aiohttp.client_exceptions.ClientResponseError):  # FIXME: normal exceptions
        await wb_manager.get_workbook(wb_id)

