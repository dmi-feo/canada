from contextlib import asynccontextmanager
import random
import string

import attr


def get_random_string(length: int = 13) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


class EntityNotFound(Exception):
    pass


@attr.s
class WBTestClient:
    client = attr.ib()

    @asynccontextmanager
    async def collection_ctx(self, title: str | None = None, parent_id: str | None = None):
        title = title or get_random_string()
        resp = await self.client.post(
            "/v1/collections",
            json={
                "title": title,
                "parentId": parent_id,
                "description": "",
            },
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
    async def workbook_ctx(self, title: str | None = None, collection_id: str | None = None):
        title = title or get_random_string()
        resp = await self.client.post(
            "/v2/workbooks",
            json={
                "title": title,
                "collectionId": collection_id,
                "description": "",
            },
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

    async def get_workbook_entries(self, workbook_id: str, scope: str | None = None) -> dict:
        params = {"scope": scope} if scope is not None else {}
        resp = await self.client.get(f"/v2/workbooks/{workbook_id}/entries", params=params)
        assert resp.status == 200
        data = await resp.json()
        return data

    async def delete_workbook(self, workbook_id: str):
        resp = await self.client.delete(f"/v2/workbooks/{workbook_id}")
        if resp.status == 404:
            raise EntityNotFound()
        assert resp.status == 200

    @asynccontextmanager
    async def entry_ctx(self, name: str, workbook_id: str, scope: str, type: str, data: dict):
        resp = await self.client.post(
            "/v1/entries",
            json={
                "name": name,
                "workbookId": workbook_id,
                "scope": scope,
                "type": type,
                "data": data,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        entry_id = data["entryId"]

        yield entry_id

        try:
            await self.delete_entry(entry_id=entry_id)
        except EntityNotFound:
            pass

    async def delete_entry(self, entry_id: str):
        resp = await self.client.delete(f"/v1/entries/{entry_id}")
        if resp.status == 404:
            raise EntityNotFound()
        assert resp.status == 200

    async def get_entry(self, entry_id: str) -> dict:
        resp = await self.client.get(f"/v1/entries/{entry_id}")
        assert resp.status == 200
        data = await resp.json()
        return data
