from canada.yt_client import SimpleYtClient
from canada.models import (
    CollectionContent, Workbook, Collection,
    Permissions, CollectionPermissions, Entry
)
from canada import constants as const


ROOT_COLLECTION_ID = "1-1161-12f-93dbdaa4"


def deserialize_workbook(raw_data: dict) -> Workbook:
    return Workbook(
        workbook_id=raw_data[const.YT_ATTR_ID],
        collection_id=raw_data[const.YT_ATTR_PARENT_ID],
        title=raw_data[const.YT_ATTR_DL_TITLE],
        description=raw_data[const.YT_ATTR_DL_DESCRIPTION],
        project_id=None,
        tenant_id=None,
        meta={},
        created_by=raw_data[const.YT_ATTR_OWNER],
        created_at=raw_data["creation_time"],
        updated_by="unknown",
        updated_at=raw_data["modification_time"],
        permissions=Permissions(
            list_access_bindings=True,
            update_access_bindings=True,
            limited_view=True,
            view=True,
            update=True,
            copy=True,
            move=True,
            publish=True,
            embed=True,
            delete=True,
        )
    )


def deserialize_collection(raw_data: dict) -> Collection:
    collection_id = raw_data[const.YT_ATTR_ID]
    return Collection(
        collection_id=collection_id,
        parent_id=raw_data[const.YT_ATTR_PARENT_ID] if collection_id != ROOT_COLLECTION_ID else None,
        title=raw_data[const.YT_ATTR_DL_TITLE] if collection_id != ROOT_COLLECTION_ID else "",
        description=raw_data[const.YT_ATTR_DL_DESCRIPTION] if collection_id != ROOT_COLLECTION_ID else "",
        project_id=None,
        tenant_id=None,
        meta={},
        created_by=raw_data[const.YT_ATTR_OWNER],
        created_at=raw_data["creation_time"],
        updated_by="unknown",
        updated_at=raw_data["modification_time"],
        permissions=CollectionPermissions(
            list_access_bindings=True,
            update_access_bindings=True,
            limited_view=True,
            view=True,
            update=True,
            copy=True,
            move=True,
            publish=True,
            embed=True,
            delete=True,
            create_collection=True,
            create_workbook=True,
        )
    )


def deserialize_entry(raw_data: dict, attributes: dict[str, str]) -> Entry:
    return Entry(
        data=raw_data.get("data", {}),
        unversioned_data=raw_data.get("unversioned_data", {}),
        entry_id=attributes[const.YT_ATTR_ID],
        workbook_id=attributes[const.YT_ATTR_PARENT_ID],
        key=attributes[const.YT_ATTR_DL_TITLE],
        permissions={"admin": True, "edit": True, "read": True, "execute": True},
        published_id=None,
        rev_id=None,
        saved_id=None,
        scope=attributes[const.YT_ATTR_DL_ENTRY_SCOPE],
        entry_type=attributes[const.YT_ATTR_DL_ENTRY_TYPE],
        tenant_id=None,
        meta={"state": "saved"},
        created_by=attributes[const.YT_ATTR_OWNER],
        created_at=attributes["creation_time"],
        updated_by="unknown",
        updated_at=attributes["modification_time"],
        hidden=False,
    )


class WBManager:
    def __init__(self, yt_cli: SimpleYtClient):
        self.yt = yt_cli
        self.root_collection_id = ROOT_COLLECTION_ID

    async def list_collection(self, coll_id: str | None = None) -> CollectionContent:
        coll_id = coll_id or self.root_collection_id
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
            if item[const.YT_LIST_ATTRS_KEY][const.YT_ATTR_DL_TYPE] == const.DL_COLLECTION_TYPE
        ]

        return CollectionContent(collections=collections, workbooks=workbooks)

    async def get_collection(self, coll_id: str) -> Collection:
        async with self.yt:
            coll_dir = await self.yt.get_node_attributes(coll_id)
        return deserialize_collection(coll_dir)

    async def create_collection(self, title: str, parent_id: str | None, description: str = "") -> str:
        parent_id = parent_id or ROOT_COLLECTION_ID
        new_node_path = f"#{parent_id}/{title}"
        async with self.yt:
            async with self.yt.transaction():
                node_id = await self.yt.create_dir(new_node_path)
                await self.yt.set_attribute(node_id, const.YT_ATTR_DL_TYPE, "collection")
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
        parent_id = collection_id or ROOT_COLLECTION_ID
        new_node_path = f"#{parent_id}/{title}"
        async with self.yt:
            async with self.yt.transaction():
                node_id = await self.yt.create_dir(new_node_path)
                await self.yt.set_attribute(node_id, const.YT_ATTR_DL_TYPE, "workbook")
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
        parent_id = workbook_id or ROOT_COLLECTION_ID
        new_node_path = f"#{parent_id}/{name}"
        async with self.yt:
            async with self.yt.transaction():
                entry_id = await self.yt.create_document(
                    node_path=new_node_path,
                    data={"data": entry_data, "unversioned_data": unversioned_data}
                )
                await self.yt.set_attribute(entry_id, const.YT_ATTR_DL_TYPE, "entry")
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
