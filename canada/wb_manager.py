from canada.yt_client import SimpleYtClient
from canada.models import CollectionContent, Workbook, Collection, Permissions,CollectionPermissions
from canada import constants as const
from canada.id import ID
from canada.tools import simplify_string


# TODO: marshmallow
def deserialize_workbook_from_list(raw_data: dict) -> Workbook:
    return Workbook(
        workbookId=raw_data["$value"],
        collectionId=None,  # FIXME
        title=raw_data["$attributes"][const.YT_ATTR_DL_TITLE],
        description=raw_data["$attributes"][const.YT_ATTR_DL_DESCRIPTION],
        projectId=None,
        tenantId=None,
        meta={},
        createdBy="TODO",  # TODO
        createdAt="2023-12-07T14:46:14.288Z",  # TODO
        updatedBy="TODO",  # TODO
        updatedAt="2023-12-07T14:46:14.288Z",  # TODO
        permissions=Permissions(
            listAccessBindings=True,
            updateAccessBindings=True,
            limitedView=True,
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
        workbookId=workbook_id,
        collectionId=parent_id,
        title=raw_data[const.YT_ATTR_DL_TITLE],
        description=raw_data[const.YT_ATTR_DL_DESCRIPTION],
        projectId=None,
        tenantId=None,
        meta={},
        createdBy="TODO",  # TODO
        createdAt="2023-12-07T14:46:14.288Z",  # TODO
        updatedBy="TODO",  # TODO
        updatedAt="2023-12-07T14:46:14.288Z",  # TODO
        permissions=Permissions(
            listAccessBindings=True,
            updateAccessBindings=True,
            limitedView=True,
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
        collectionId=collection_id,
        parentId=parent_collection_id,
        title=raw_data["$attributes"][const.YT_ATTR_DL_TITLE],
        description=raw_data["$attributes"][const.YT_ATTR_DL_DESCRIPTION],
        projectId=None,
        tenantId=None,
        meta={},
        createdBy="TODO",  # TODO
        createdAt="2023-12-07T14:46:14.288Z",  # TODO§
        updatedBy="TODO",  # TODO
        updatedAt="2023-12-07T14:46:14.288Z",  # TODO
        permissions=CollectionPermissions(
            listAccessBindings=True,
            updateAccessBindings=True,
            limitedView=True,
            view=True,
            update=True,
            copy=True,
            move=True,
            publish=True,
            embed=True,
            delete=True,
            createCollection=True,
            createWorkbook=True,
        )
    )


def deserialize_collection(raw_data: dict, collection_id: ID) -> Collection:
    parent_id = collection_id.get_parent()
    return Collection(
        collectionId=collection_id,
        parentId=parent_id,
        title=raw_data[const.YT_ATTR_DL_TITLE],
        description=raw_data[const.YT_ATTR_DL_DESCRIPTION],
        projectId=None,
        tenantId=None,
        meta={},
        createdBy="TODO",  # TODO
        createdAt="2023-12-07T14:46:14.288Z",  # TODO§
        updatedBy="TODO",  # TODO
        updatedAt="2023-12-07T14:46:14.288Z",  # TODO
        permissions=CollectionPermissions(
            listAccessBindings=True,
            updateAccessBindings=True,
            limitedView=True,
            view=True,
            update=True,
            copy=True,
            move=True,
            publish=True,
            embed=True,
            delete=True,
            createCollection=True,
            createWorkbook=True,
        )
    )


class WBManager:
    def __init__(self, yt_cli: SimpleYtClient):
        self.yt = yt_cli

    async def list_collection(self, coll_id: ID | None = None) -> CollectionContent:
        path = coll_id.to_path()
        async with self.yt:
            dirs = await self.yt.list_dir(path, attributes=const.YT_ATTR_ALL)

        workbooks = [
            deserialize_workbook_from_list(item)
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
        node_id = parent_id.add(simplify_string(title))

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
        node_id = collection_id.add(simplify_string(title))

        async with self.yt:
            async with self.yt.transaction():
                await self.yt.create_dir(node_id.to_path())
                await self.yt.set_attribute(node_id.to_path(), const.YT_ATTR_DL_TYPE, "workbook")
                await self.yt.set_attribute(node_id.to_path(), const.YT_ATTR_DL_TITLE, title)
                await self.yt.set_attribute(node_id.to_path(), const.YT_ATTR_DL_DESCRIPTION, description)

        return node_id