from canada.wb_manager.deserialization import deserialize_workbook, deserialize_collection, deserialize_entry
from canada.wb_manager.exc import RootCollectionCannotBeRequested
from canada.yt_client import SimpleYtClient
from canada.models import (
    CollectionContent, Workbook, Collection,
    Entry
)
from canada import constants as const


class WBManager:
    def __init__(self, yt_cli: SimpleYtClient, root_collection_node_id: str):
        self.yt = yt_cli
        self.root_collection_node_id = root_collection_node_id

    async def list_collection(self, coll_id: str | None = None) -> CollectionContent:
        coll_id = coll_id or self.root_collection_node_id
        async with self.yt:
            dirs = await self.yt.list_dir(coll_id, attributes=const.YT_ATTRS_TO_REQ)

        workbooks = [
            deserialize_workbook(item[const.YT_LIST_ATTRS_KEY])
            for item in dirs
            if item[const.YT_LIST_ATTRS_KEY][const.YT_ATTR_DL_TYPE] == const.DL_WORKBOOK_TYPE
        ]

        collections = [
            deserialize_collection(item[const.YT_LIST_ATTRS_KEY])
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

        async with self.yt:
            coll_dir = await self.yt.get_node_attributes(coll_id)
        return deserialize_collection(coll_dir)

    async def create_collection(self, title: str, parent_id: str | None, description: str = "") -> str:
        parent_id = parent_id or self.root_collection_node_id
        new_node_path = f"#{parent_id}/{title}"
        async with self.yt:
            async with self.yt.transaction():
                node_id = await self.yt.create_dir(new_node_path)
                await self.yt.set_attribute(node_id, const.YT_ATTR_DL_TYPE, const.DL_COLLECTION_TYPE)
                await self.yt.set_attribute(node_id, const.YT_ATTR_DL_TITLE, title)
                await self.yt.set_attribute(node_id, const.YT_ATTR_DL_DESCRIPTION, description)

        return node_id

    async def delete_collection(self, collection_id: str):
        async with self.yt:
            await self.yt.delete_node(collection_id)

    async def get_workbook(self, wb_id: str) -> Workbook:
        async with self.yt:
            wb_dir = await self.yt.get_node_attributes(wb_id)
        return deserialize_workbook(wb_dir)

    async def create_workbook(self, title: str, collection_id: str, description: str = "") -> str:
        parent_id = collection_id or self.root_collection_node_id
        new_node_path = f"#{parent_id}/{title}"
        async with self.yt:
            async with self.yt.transaction():
                node_id = await self.yt.create_dir(new_node_path)
                await self.yt.set_attribute(node_id, const.YT_ATTR_DL_TYPE, const.DL_WORKBOOK_TYPE)
                await self.yt.set_attribute(node_id, const.YT_ATTR_DL_TITLE, title)
                await self.yt.set_attribute(node_id, const.YT_ATTR_DL_DESCRIPTION, description)

        return node_id

    async def get_workbook_entries(self, wb_id: str) -> list[Entry]:
        async with self.yt:
            dir_objects = await self.yt.list_dir(wb_id, attributes=const.YT_ATTRS_TO_REQ)

        return [deserialize_entry(item, attributes=item[const.YT_LIST_ATTRS_KEY]) for item in dir_objects]

    async def get_entry(self, entry_id: str) -> Entry:
        async with self.yt:
            raw_data = await self.yt.read_document(entry_id)
            attributes = await self.yt.get_node_attributes(entry_id)

        return deserialize_entry(raw_data, attributes=attributes)

    async def create_entry(
            self, name: str, workbook_id: str, entry_data: dict, unversioned_data: dict,
            scope: str, entry_type: str
    ) -> str:
        parent_id = workbook_id or self.root_collection_node_id
        new_node_path = f"#{parent_id}/{name}"
        async with self.yt:
            async with self.yt.transaction():
                entry_id = await self.yt.create_document(
                    node_path=new_node_path,
                    data={"data": entry_data, "unversioned_data": unversioned_data}
                )
                await self.yt.set_attribute(entry_id, const.YT_ATTR_DL_TYPE, const.DL_ENTRY_TYPE)
                await self.yt.set_attribute(entry_id, const.YT_ATTR_DL_TITLE, name)
                await self.yt.set_attribute(entry_id, const.YT_ATTR_DL_ENTRY_SCOPE, scope)
                await self.yt.set_attribute(entry_id, const.YT_ATTR_DL_ENTRY_TYPE, entry_type)

        return entry_id

    async def update_entry(self, entry_id: str, entry_data: dict | None, unversioned_data: dict | None):
        async with self.yt:
            async with self.yt.transaction():
                raw_data = await self.yt.read_document(entry_id)
                attributes = await self.yt.get_node_attributes(entry_id)
                curr_entry = deserialize_entry(raw_data, attributes=attributes)

                new_data = entry_data if entry_data is not None else curr_entry.data
                new_unversioned_data = unversioned_data if unversioned_data is not None else curr_entry.unversioned_data
                await self.yt.write_document(
                    node_id=entry_id,
                    data={"data": new_data, "unversioned_data": new_unversioned_data}
                )
