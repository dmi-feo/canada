from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

import attr

from canada import constants
from canada.models import Workbook, Collection, Entry, ModificationInfo


@attr.s
class SerializableEntity:
    title: str = attr.ib()
    node_type: constants.YTNodeType = attr.ib()
    data: dict | None = attr.ib()
    attributes: dict[str, str] | None = attr.ib()


class BaseCanadaStorageSerializer(ABC):
    @abstractmethod
    def serialize_collection(self, collection: Collection) -> SerializableEntity:
        pass

    @abstractmethod
    def deserialize_collection(self, raw_data: dict) -> Collection:
        pass

    @abstractmethod
    def serialize_workbook(self, workbook: Workbook) -> SerializableEntity:
        pass

    @abstractmethod
    def deserialize_workbook(self, raw_data: dict) -> Workbook:
        pass

    @abstractmethod
    def serialize_entry(self, entry: Entry) -> SerializableEntity:
        pass

    @abstractmethod
    def deserialize_entry(self, raw_data: dict, attributes: dict[str, str]) -> Entry:
        pass


class SimpleCanadaStorageSerializer(BaseCanadaStorageSerializer):
    YT_DOCUMENT_DATA_KEY: ClassVar[str] = "data"
    YT_DOCUMENT_UNVERSIONED_DATA_KEY: ClassVar[str] = "unversioned_data"

    def serialize_collection(self, collection: Collection) -> SerializableEntity:
        return SerializableEntity(
            title=collection.title,
            node_type=constants.YTNodeType.map_node,
            data=None,
            attributes={
                constants.YT_ATTR_DL_TYPE: constants.DL_COLLECTION_TYPE,
            },
        )

    def deserialize_collection(self, raw_data: dict) -> Collection:
        collection_id = raw_data[constants.YT_ATTR_ID]

        return Collection(
            collection_id=collection_id,
            parent_id=raw_data[constants.YT_ATTR_PARENT_ID],
            title=raw_data[constants.YT_ATTR_KEY],
            modification_info=ModificationInfo(
                created_by=raw_data[constants.YT_ATTR_OWNER],
                created_at=raw_data[constants.YT_ATTR_CREATION_TIME],
                updated_by="unknown",
                updated_at=raw_data[constants.YT_ATTR_MOD_TIME],
            ),
        )

    def serialize_workbook(self, workbook: Workbook) -> SerializableEntity:
        return SerializableEntity(
            title=workbook.title,
            node_type=constants.YTNodeType.map_node,
            data=None,
            attributes={
                constants.YT_ATTR_DL_TYPE: constants.DL_WORKBOOK_TYPE,
            },
        )

    def deserialize_workbook(self, raw_data: dict) -> Workbook:
        return Workbook(
            workbook_id=raw_data[constants.YT_ATTR_ID],
            collection_id=raw_data[constants.YT_ATTR_PARENT_ID],
            title=raw_data[constants.YT_ATTR_KEY],
            modification_info=ModificationInfo(
                created_by=raw_data[constants.YT_ATTR_OWNER],
                created_at=raw_data[constants.YT_ATTR_CREATION_TIME],
                updated_by="unknown",
                updated_at=raw_data[constants.YT_ATTR_MOD_TIME],
            ),
        )

    def serialize_entry(self, entry: Entry) -> SerializableEntity:
        return SerializableEntity(
            title=entry.key,
            node_type=constants.YTNodeType.document,
            data={
                self.YT_DOCUMENT_DATA_KEY: entry.data,
                self.YT_DOCUMENT_UNVERSIONED_DATA_KEY: entry.unversioned_data,
            },
            attributes={
                constants.YT_ATTR_DL_TYPE: constants.DL_ENTRY_TYPE,
                constants.YT_ATTR_DL_ENTRY_SCOPE: entry.scope,
                constants.YT_ATTR_DL_ENTRY_TYPE: entry.entry_type,
            },
        )

    def deserialize_entry(self, raw_data: dict, attributes: dict[str, str]) -> Entry:
        return Entry(
            data=raw_data.get(self.YT_DOCUMENT_DATA_KEY, {}),
            unversioned_data=raw_data.get(self.YT_DOCUMENT_UNVERSIONED_DATA_KEY, {}),
            entry_id=attributes[constants.YT_ATTR_ID],
            workbook_id=attributes[constants.YT_ATTR_PARENT_ID],
            key=attributes[constants.YT_ATTR_KEY],
            scope=attributes[constants.YT_ATTR_DL_ENTRY_SCOPE],
            entry_type=attributes[constants.YT_ATTR_DL_ENTRY_TYPE],
            meta={"state": "saved"},
            modification_info=ModificationInfo(
                created_by=attributes[constants.YT_ATTR_OWNER],
                created_at=attributes[constants.YT_ATTR_CREATION_TIME],
                updated_by="unknown",
                updated_at=attributes[constants.YT_ATTR_MOD_TIME],
            ),
        )
