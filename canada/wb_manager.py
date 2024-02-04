import json
from typing import Type

import marshmallow as ma

from canada.yt_client import SimpleYtClient
from canada.models import (
    CollectionContent, Workbook, Collection,
    Permissions, CollectionPermissions, Entry, BaseUSEntity
)
from canada import constants as const
from canada.id import ID
from canada.tools import slugify


# TODO: marshmallow
def deserialize_workbook_from_list(raw_data: dict, parent_collection_id: ID) -> Workbook:
    workbook_id = parent_collection_id.add(raw_data["$value"])
    return Workbook(
        workbook_id=workbook_id,
        collection_id=parent_collection_id,
        title=raw_data["$attributes"][const.YT_ATTR_DL_TITLE],
        description=raw_data["$attributes"][const.YT_ATTR_DL_DESCRIPTION],
        project_id=None,
        tenant_id=None,
        meta={},
        created_by="TODO",  # TODO
        created_at="2023-12-07T14:46:14.288Z",  # TODO
        updated_by="TODO",  # TODO
        updated_at="2023-12-07T14:46:14.288Z",  # TODO
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


def deserialize_workbook(raw_data: dict, workbook_id: ID) -> Workbook:
    parent_id = workbook_id.get_parent()
    return Workbook(
        workbook_id=workbook_id,
        collection_id=parent_id,
        title=raw_data[const.YT_ATTR_DL_TITLE],
        description=raw_data[const.YT_ATTR_DL_DESCRIPTION],
        project_id=None,
        tenant_id=None,
        meta={},
        created_by="TODO",  # TODO
        created_at="2023-12-07T14:46:14.288Z",  # TODO
        updated_by="TODO",  # TODO
        updated_at="2023-12-07T14:46:14.288Z",  # TODO
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


def deserialize_collection_from_list(raw_data: dict, parent_collection_id: ID) -> Collection:
    collection_id = parent_collection_id.add(raw_data["$value"])
    return Collection(
        collection_id=collection_id,
        parent_id=parent_collection_id,
        title=raw_data["$attributes"][const.YT_ATTR_DL_TITLE],
        description=raw_data["$attributes"][const.YT_ATTR_DL_DESCRIPTION],
        project_id=None,
        tenant_id=None,
        meta={},
        created_by="TODO",  # TODO
        created_at="2023-12-07T14:46:14.288Z",  # TODO§
        updated_by="TODO",  # TODO
        updated_at="2023-12-07T14:46:14.288Z",  # TODO
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


def deserialize_collection(raw_data: dict, collection_id: ID) -> Collection:
    parent_id = collection_id.get_parent()
    return Collection(
        collection_id=collection_id,
        parent_id=parent_id,
        title=raw_data[const.YT_ATTR_DL_TITLE],
        description=raw_data[const.YT_ATTR_DL_DESCRIPTION],
        project_id=None,
        tenant_id=None,
        meta={},
        created_by="TODO",  # TODO
        created_at="2023-12-07T14:46:14.288Z",  # TODO§
        updated_by="TODO",  # TODO
        updated_at="2023-12-07T14:46:14.288Z",  # TODO
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


class BaseStorageSchema[T](ma.Schema):
    TARGET_TYPE = Type[BaseUSEntity]

    def load_object(self, *args, **kwargs) -> T:
        return self.TARGET_TYPE(**self.loads(*args, **kwargs))


class EntryStorageSchema[Entry](BaseStorageSchema):
    TARGET_TYPE = Entry

    created_at = ma.fields.String(data_key="creation_time")
    updated_at = ma.fields.String(data_key="modification_time")
    created_by = ma.fields.String(missing=None)
    data = ma.fields.Dict(missing=None)
    entry_id = ma.fields.String(data_key="entryId")
    key = ma.fields.String()
    meta = ma.fields.Dict()
    permissions = ma.fields.Dict()
    published_id = ma.fields.String(data_key="publishedId")
    rev_id = ma.fields.String(data_key="revId")
    saved_id = ma.fields.String(data_key="savedId")
    scope = ma.fields.String()
    type_ = ma.fields.String(data_key="type")
    workbook_id = ma.fields.String(data_key="workbookId")
    unversioned_data = ma.fields.Dict(data_key="unversionedData")


def deserialize_entry_from_list(raw_data: dict, workbook_id: ID) -> Entry:
    entry_id = workbook_id.add(raw_data["$value"])

    return Entry(
        data={},
        unversioned_data={},
        entry_id=entry_id,
        workbook_id=workbook_id,
        key=raw_data["$attributes"][const.YT_ATTR_DL_TITLE],
        permissions={"admin": True, "edit": True, "read": True, "execute": True},
        published_id=ID.empty(),
        rev_id=ID.empty(),
        saved_id=ID.empty(),
        scope=raw_data["$attributes"][const.YT_ATTR_DL_ENTRY_SCOPE],
        entry_type=raw_data["$attributes"][const.YT_ATTR_DL_ENTRY_TYPE],
        tenant_id=None,
        meta={"state": "saved"},
        created_by="SOMEONE",
        created_at=raw_data["$attributes"]["creation_time"],
        updated_by="SOMEONE",
        updated_at=raw_data["$attributes"]["modification_time"],
        hidden=False,
    )


def deserialize_entry(raw_data: dict, entry_id: ID, attributes: dict[str, str]) -> Entry:
    workbook_id = entry_id.get_parent()
    return Entry(
        data=raw_data["data"],
        unversioned_data=raw_data["unversioned_data"],
        entry_id=entry_id,
        workbook_id=workbook_id,
        key=attributes[const.YT_ATTR_DL_TITLE],
        permissions={"admin": True, "edit": True, "read": True, "execute": True},
        published_id=ID.empty(),
        rev_id=ID.empty(),
        saved_id=ID.empty(),
        scope=attributes[const.YT_ATTR_DL_ENTRY_SCOPE],
        entry_type=attributes[const.YT_ATTR_DL_ENTRY_TYPE],
        tenant_id=None,
        meta={"state": "saved"},
        created_by="SOMEONE",
        created_at=attributes["creation_time"],
        updated_by="SOMEONE",
        updated_at=attributes["modification_time"],
        hidden=False,
    )


class WBManager:
    def __init__(self, yt_cli: SimpleYtClient):
        self.yt = yt_cli

    async def list_collection(self, coll_id: ID | None = None) -> CollectionContent:
        path = coll_id.to_path()
        async with self.yt:
            dirs = await self.yt.list_dir(path, attributes=const.YT_ATTR_DL_ALL)

        workbooks = [
            deserialize_workbook_from_list(item, parent_collection_id=coll_id)
            for item in dirs
            if item["$attributes"][const.YT_ATTR_DL_TYPE] == const.DL_WORKBOOK_TYPE
        ]

        collections = [
            deserialize_collection_from_list(item, parent_collection_id=coll_id)
            for item in dirs
            if item["$attributes"][const.YT_ATTR_DL_TYPE] == const.DL_COLLECTION_TYPE
        ]

        return CollectionContent(collections=collections, workbooks=workbooks)

    async def get_collection(self, coll_id: ID) -> Collection:
        async with self.yt:
            coll_dir = await self.yt.get_node(coll_id.to_path())
        return deserialize_collection(coll_dir, collection_id=coll_id)

    async def create_collection(self, title: str, parent_id: ID, description: str = "") -> ID:
        node_id = parent_id.add(slugify(title))

        async with self.yt:
            async with self.yt.transaction():
                await self.yt.create_dir(node_id.to_path())
                await self.yt.set_attribute(node_id.to_path(), const.YT_ATTR_DL_TYPE, "collection")
                await self.yt.set_attribute(node_id.to_path(), const.YT_ATTR_DL_TITLE, title)
                await self.yt.set_attribute(node_id.to_path(), const.YT_ATTR_DL_DESCRIPTION, description)

        return node_id

    async def delete_collection(self, collection_id: ID):
        async with self.yt:
            await self.yt.delete_node(collection_id.to_path())

    async def get_workbook(self, wb_id: ID) -> Workbook:
        async with self.yt:
            wb_dir = await self.yt.get_node(wb_id.to_path())
        return deserialize_workbook(wb_dir, workbook_id=wb_id)

    async def create_workbook(self, title: str, collection_id: ID, description: str = "") -> ID:
        node_id = collection_id.add(slugify(title))

        async with self.yt:
            async with self.yt.transaction():
                await self.yt.create_dir(node_id.to_path())
                await self.yt.set_attribute(node_id.to_path(), const.YT_ATTR_DL_TYPE, "workbook")
                await self.yt.set_attribute(node_id.to_path(), const.YT_ATTR_DL_TITLE, title)
                await self.yt.set_attribute(node_id.to_path(), const.YT_ATTR_DL_DESCRIPTION, description)

        return node_id

    async def get_workbook_entries(self, wb_id: ID) -> list[Entry]:
        async with self.yt:
            dir_objects = await self.yt.list_dir(wb_id.to_path(), attributes=const.YT_ATTRS_TO_REQ)

        return [deserialize_entry_from_list(item, workbook_id=wb_id) for item in dir_objects]

    async def get_entry(self, entry_id: ID) -> Entry:
        async with self.yt:
            raw_data_str = await self.yt.read_file(entry_id.to_path())
            attributes = await self.yt.get_node(entry_id.to_path())

        raw_data = json.loads(raw_data_str)
        return deserialize_entry(raw_data, entry_id=entry_id, attributes=attributes)

    async def create_entry(
            self, name: str, workbook_id: ID, entry_data: dict, unversioned_data: dict,
            scope: str, entry_type: str
    ) -> ID:
        entry_id = workbook_id.add(slugify(name))
        async with self.yt:
            async with self.yt.transaction():
                await self.yt.create_file(file_path=entry_id.to_path())
                await self.yt.write_file(
                    file_path=entry_id.to_path(),
                    file_data={"data": entry_data, "unversioned_data": unversioned_data}
                )
                await self.yt.set_attribute(entry_id.to_path(), const.YT_ATTR_DL_TYPE, "entry")
                await self.yt.set_attribute(entry_id.to_path(), const.YT_ATTR_DL_TITLE, name)
                await self.yt.set_attribute(entry_id.to_path(), const.YT_ATTR_DL_ENTRY_SCOPE, scope)
                await self.yt.set_attribute(entry_id.to_path(), const.YT_ATTR_DL_ENTRY_TYPE, entry_type)

        return entry_id

    async def update_entry(self, entry_id: ID, entry_data: dict | None, unversioned_data: dict | None):
        async with self.yt:
            async with self.yt.transaction():
                curr_entry = await self.get_entry(entry_id)
                new_data = entry_data if entry_data is not None else curr_entry.data
                new_unversioned_data = unversioned_data if unversioned_data is not None else curr_entry.unversioned_data
                await self.yt.write_file(
                    file_path=entry_id.to_path(),
                    file_data={"data": new_data, "unversioned_data": new_unversioned_data}
                )
