from contextlib import asynccontextmanager

import attr


class EntityNotFound(Exception):
    pass


@attr.s
class WBTestClient:
    client = attr.ib()

    @asynccontextmanager
    async def collection_ctx(self, title: str = "test_collection", parent_id: str | None = None):
        resp = await self.client.post(
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
            await self.delete_collection(collection_id=coll_id)
        except EntityNotFound:
            pass

    async def get_collection(self, collection_id: str) -> dict:
        resp = await self.client.get(f"/v1/collections/{collection_id}")
        assert resp.status == 200
        data = await resp.json()
        return data

    async def delete_collection(self, collection_id: str):
        resp = await self.client.delete(f"/v1/collections/{collection_id}")
        if resp.status == 404:
            raise EntityNotFound()
        assert resp.status == 200

    @asynccontextmanager
    async def workbook_ctx(self, title: str = "test_workbook", collection_id: str | None = None):
        resp = await self.client.post(
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
            await self.delete_workbook(workbook_id=wb_id)
        except EntityNotFound:
            pass

    async def get_workbook(self, workbook_id: str) -> dict:
        resp = await self.client.get(f"/v2/workbooks/{workbook_id}")
        assert resp.status == 200
        data = await resp.json()
        return data

    async def delete_workbook(self, workbook_id: str):
        resp = await self.client.delete(f"/v2/workbooks/{workbook_id}")
        if resp.status == 404:
            raise EntityNotFound()
        assert resp.status == 200
