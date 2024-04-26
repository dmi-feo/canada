from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

import aiohttp
import attr

from canada.base_wb_manager.base_wb_manager import BaseWorkbookManager
from canada.base_wb_manager.exc import WBManagerStorageError
from canada.constants import CanadaEntityType
from canada.models import (
    Collection,
    CollectionContent,
    Entry,
    Workbook,
)
from canada.yt_wb_manager import constants as yt_const
from canada.yt_wb_manager.exc import RootCollectionCannotBeRequested
from canada.yt_wb_manager.serialization import SerializableEntity
from canada.yt_wb_manager.yt_client.exc import YtServerError
from canada.yt_wb_manager.yt_client.yt_client import SimpleYtClient


if TYPE_CHECKING:
    from canada.types import JSONDict
    from canada.yt_wb_manager.serialization import BaseCanadaStorageSerializer


class WBAwareYtClient(SimpleYtClient):
    async def make_request(self, *args: Any, **kwargs: Any) -> aiohttp.ClientResponse:
        try:
            return await super().make_request(*args, **kwargs)
        except YtServerError as err:
            raise WBManagerStorageError(message=err.message) from err


@attr.s
class YTWorkbookManager(BaseWorkbookManager):
    yt_client: WBAwareYtClient = attr.ib()
    root_collection_node_id: str = attr.ib()
    serializer: BaseCanadaStorageSerializer = attr.ib()

    async def list_collection(self, coll_id: str | None = None) -> CollectionContent:
        if coll_id is None:
            coll_id = self.root_collection_node_id

        async with self.yt_client:
            dir_nodes = await self.yt_client.list_dir(coll_id, attributes=yt_const.YT_ATTRS_TO_REQ)

        workbooks = [
            self.serializer.deserialize_workbook(SerializableEntity(title=node.name, attributes=node.attributes))
            for node in dir_nodes
            if (
                node.attributes.get(yt_const.YTAttributes.DL_TYPE.value, CanadaEntityType.workbook.value)
                == CanadaEntityType.workbook.value
            )
        ]

        collections = [
            self.serializer.deserialize_collection(SerializableEntity(title=node.name, attributes=node.attributes))
            for node in dir_nodes
            if (
                (node.attributes.get(yt_const.YTAttributes.DL_TYPE.value) == CanadaEntityType.collection.value)
                and (node.attributes[yt_const.YTAttributes.ID.value] != self.root_collection_node_id)
            )
        ]

        return CollectionContent(collections=collections, workbooks=workbooks)

    async def get_collection(self, coll_id: str) -> Collection:
        if coll_id == self.root_collection_node_id:
            raise RootCollectionCannotBeRequested()

        async with self.yt_client:
            coll_dir_attrs = await self.yt_client.get_node_attributes(coll_id)
        return self.serializer.deserialize_collection(
            SerializableEntity(
                title=coll_dir_attrs[yt_const.YTAttributes.KEY.value],
                attributes=coll_dir_attrs,
            )
        )

    async def create_collection(self, collection: Collection) -> str:
        if collection.parent_id is None:
            parent_id = self.root_collection_node_id
        else:
            parent_id = collection.parent_id

        new_node_path = f"#{parent_id}/{collection.title}"
        serialized = self.serializer.serialize_collection(collection)
        async with self.yt_client:
            async with self.yt_client.transaction() as tx_id:
                node_id = await self.yt_client.create_node(
                    new_node_path, node_type=yt_const.YTNodeType.map_node, tx_id=tx_id
                )
                for attr_key, attr_value in serialized.attributes.items():
                    await self.yt_client.set_attribute(node_id, attr_key, attr_value, tx_id=tx_id)

        return node_id

    async def delete_collection(self, coll_id: str) -> None:
        async with self.yt_client:
            await self.yt_client.delete_node(coll_id)

    async def get_workbook(self, wb_id: str) -> Workbook:
        async with self.yt_client:
            wb_dir_attrs = await self.yt_client.get_node_attributes(wb_id)
        return self.serializer.deserialize_workbook(
            SerializableEntity(
                title=wb_dir_attrs[yt_const.YTAttributes.KEY.value],
                attributes=wb_dir_attrs,
            )
        )

    async def create_workbook(self, workbook: Workbook) -> str:
        if workbook.collection_id is None:
            parent_id = self.root_collection_node_id
        else:
            parent_id = workbook.collection_id

        new_node_path = f"#{parent_id}/{workbook.title}"
        serialized = self.serializer.serialize_workbook(workbook)
        async with self.yt_client:
            async with self.yt_client.transaction() as tx_id:
                node_id = await self.yt_client.create_node(
                    new_node_path, node_type=yt_const.YTNodeType.map_node, tx_id=tx_id
                )
                for attr_key, attr_value in serialized.attributes.items():
                    await self.yt_client.set_attribute(node_id, attr_key, attr_value, tx_id=tx_id)

        return node_id

    async def get_workbook_entries(self, wb_id: str, scope: str | None) -> list[Entry]:
        async with self.yt_client:
            dir_nodes = await self.yt_client.list_dir(wb_id, attributes=yt_const.YT_ATTRS_TO_REQ)

        return [
            self.serializer.deserialize_entry(SerializableEntity(title=node.name, attributes=node.attributes))
            for node in dir_nodes
            if (
                node.attributes.get(yt_const.YTAttributes.DL_TYPE.value) == CanadaEntityType.entry.value
                and (
                    # there must have been `search` method in cypress with filtration
                    # but no trace of it in doc...
                    node.attributes.get(yt_const.YTAttributes.DL_ENTRY_SCOPE.value) == scope
                    or scope is None
                )
            )
        ]

    async def delete_workbook(self, wb_id: str) -> None:
        async with self.yt_client:
            await self.yt_client.delete_node(wb_id)

    async def get_entry(self, entry_id: str) -> Entry:
        async with self.yt_client:
            raw_data = await self.yt_client.read_document(entry_id)
            attributes = await self.yt_client.get_node_attributes(entry_id)

        assert isinstance(raw_data, dict)
        return self.serializer.deserialize_entry(
            SerializableEntity(
                title=attributes[yt_const.YTAttributes.KEY.value],
                attributes=attributes,
                data=raw_data,
            )
        )

    async def create_entry(self, entry: Entry) -> str:
        new_node_path = f"#{entry.workbook_id}/{entry.title}"
        serialized = self.serializer.serialize_entry(entry)
        async with self.yt_client:
            async with self.yt_client.transaction() as tx_id:
                node_id = await self.yt_client.create_node(
                    path=new_node_path,
                    node_type=yt_const.YTNodeType.document,
                    attributes={"value": serialized.data},
                    tx_id=tx_id,
                )
                for attr_key, attr_value in serialized.attributes.items():
                    await self.yt_client.set_attribute(node_id, attr_key, attr_value, tx_id=tx_id)

        return node_id

    async def update_entry(
        self,
        entry_id: str,
        entry_data: JSONDict | None,
        unversioned_data: JSONDict | None,
        lock_token: str | None = None,
    ) -> None:
        running_tx_id = lock_token
        async with self.yt_client:
            async with self.yt_client.transaction(outer_tx_id=running_tx_id) as tx_id:
                raw_data = await self.yt_client.read_document(entry_id, tx_id=tx_id)
                assert isinstance(raw_data, dict)
                attributes = await self.yt_client.get_node_attributes(entry_id, tx_id=tx_id)
                curr_entry = self.serializer.deserialize_entry(
                    SerializableEntity(
                        title=attributes[yt_const.YTAttributes.KEY.value],
                        attributes=attributes,
                        data=raw_data,
                    )
                )

                curr_entry.data = entry_data if entry_data is not None else curr_entry.data
                curr_entry.unversioned_data = (
                    unversioned_data if unversioned_data is not None else curr_entry.unversioned_data
                )

                serialized = self.serializer.serialize_entry(curr_entry)
                assert serialized.data is not None
                await self.yt_client.write_document(node_id=entry_id, data=serialized.data, tx_id=tx_id)

    async def delete_entry(self, entry_id: str) -> None:
        async with self.yt_client:
            await self.yt_client.delete_node(node_id=entry_id)

    async def set_lock(self, entry_id: str, duration: int | None = None, force: bool | None = None) -> str:
        async with self.yt_client:
            tx_id = await self.yt_client.start_transaction()
            await self.yt_client.set_lock(entry_id, tx_id=tx_id, mode=yt_const.YTLockMode.exclusive)
        return tx_id  # we have to finish the transaction on lock release, and we don't care about lock_token at all

    async def delete_lock(self, entry_id: str, lock_token: str) -> None:
        tx_id = lock_token  # that's how it is
        async with self.yt_client:
            await self.yt_client.commit_transaction(tx_id)
