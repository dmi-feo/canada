from __future__ import annotations

from typing import TYPE_CHECKING

import attr

from canada.wb_manager.exc import RootCollectionCannotBeRequested
from canada.wb_manager.yt_client.yt_client import SimpleYtClient
from canada.models import CollectionContent, Workbook, Collection, Entry
from canada import constants as const
from canada.base_wb_manager import BaseWorkbookManager

if TYPE_CHECKING:
    from canada.wb_manager.serialization import BaseCanadaStorageSerializer


@attr.s
class YTWorkbookManager(BaseWorkbookManager):
    yt_client: SimpleYtClient = attr.ib()
    root_collection_node_id: str = attr.ib()
    serializer: BaseCanadaStorageSerializer = attr.ib()

    async def list_collection(self, coll_id: str | None = None) -> CollectionContent:
        coll_id = coll_id or self.root_collection_node_id
        async with self.yt_client:
            dirs = await self.yt_client.list_dir(coll_id, attributes=const.YT_ATTRS_TO_REQ)

        workbooks = [
            self.serializer.deserialize_workbook(item[const.YT_LIST_ATTRS_KEY])
            for item in dirs
            if item[const.YT_LIST_ATTRS_KEY][const.YT_ATTR_DL_TYPE] == const.DL_WORKBOOK_TYPE
        ]

        collections = [
            self.serializer.deserialize_collection(item[const.YT_LIST_ATTRS_KEY])
            for item in dirs
            if (
                    item[const.YT_LIST_ATTRS_KEY][const.YT_ATTR_DL_TYPE] == const.DL_COLLECTION_TYPE and
                    item[const.YT_LIST_ATTRS_KEY][const.YT_ATTR_ID] != self.root_collection_node_id
            )
        ]

        return CollectionContent(collections=collections, workbooks=workbooks)

    async def get_collection(self, coll_id: str) -> Collection:
        if coll_id == self.root_collection_node_id:
            raise RootCollectionCannotBeRequested()

        async with self.yt_client:
            coll_dir = await self.yt_client.get_node_attributes(coll_id)
        return self.serializer.deserialize_collection(coll_dir)

    async def create_collection(self, collection: Collection):
        parent_id = collection.parent_id or self.root_collection_node_id
        new_node_path = f"#{parent_id}/{collection.title}"
        serialized = self.serializer.serialize_collection(collection)
        async with self.yt_client:
            async with self.yt_client.transaction():
                node_id = await self.yt_client.create_dir(new_node_path)
                for attr_key, attr_value in serialized.attributes.items():
                    await self.yt_client.set_attribute(node_id, attr_key, attr_value)

        return node_id

    async def delete_collection(self, coll_id: str):
        async with self.yt_client:
            await self.yt_client.delete_node(coll_id)

    async def get_workbook(self, wb_id: str) -> Workbook:
        async with self.yt_client:
            wb_dir = await self.yt_client.get_node_attributes(wb_id)
        return self.serializer.deserialize_workbook(wb_dir)

    async def create_workbook(self, workbook: Workbook) -> str:
        parent_id = workbook.collection_id or self.root_collection_node_id
        new_node_path = f"#{parent_id}/{workbook.title}"
        serialized = self.serializer.serialize_workbook(workbook)
        async with self.yt_client:
            async with self.yt_client.transaction():
                node_id = await self.yt_client.create_dir(new_node_path)
                for attr_key, attr_value in serialized.attributes.items():
                    await self.yt_client.set_attribute(node_id, attr_key, attr_value)

        return node_id

    async def get_workbook_entries(self, wb_id: str) -> list[Entry]:
        async with self.yt_client:
            dir_objects = await self.yt_client.list_dir(wb_id, attributes=const.YT_ATTRS_TO_REQ)

        return [
            self.serializer.deserialize_entry(item, attributes=item[const.YT_LIST_ATTRS_KEY])
            for item in dir_objects
        ]

    async def get_entry(self, entry_id: str) -> Entry:
        async with self.yt_client:
            raw_data = await self.yt_client.read_document(entry_id)
            attributes = await self.yt_client.get_node_attributes(entry_id)

        return self.serializer.deserialize_entry(raw_data, attributes=attributes)

    async def create_entry(self, entry: Entry) -> str:
        new_node_path = f"#{entry.workbook_id}/{entry.title}"
        serialized = self.serializer.serialize_entry(entry)
        async with self.yt_client:
            async with self.yt_client.transaction():
                node_id = await self.yt_client.create_document(
                    node_path=new_node_path,
                    data=serialized.data,
                )
                for attr_key, attr_value in serialized.attributes.items():
                    await self.yt_client.set_attribute(node_id, attr_key, attr_value)

        return node_id

    async def update_entry(self, entry_id: str, entry_data: dict | None, unversioned_data: dict | None):
        async with self.yt_client:
            async with self.yt_client.transaction():
                raw_data = await self.yt_client.read_document(entry_id)
                attributes = await self.yt_client.get_node_attributes(entry_id)
                curr_entry = self.serializer.deserialize_entry(raw_data, attributes=attributes)

                curr_entry.data = entry_data if entry_data is not None else curr_entry.data
                curr_entry.unversioned_data = (
                    unversioned_data
                    if unversioned_data is not None
                    else curr_entry.unversioned_data
                )

                serialized = self.serializer.serialize_entry(curr_entry)
                await self.yt_client.write_document(
                    node_id=entry_id,
                    data=serialized.data,
                )
