from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

import attr

from canada.constants import CanadaEntityType
from canada.yt_wb_manager import constants as yt_const
from canada.models import Workbook, Collection, Entry, ModificationInfo


@attr.s
class SerializableEntity:
    title: str = attr.ib()
    node_type: yt_const.YTNodeType = attr.ib()
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


@attr.s
class SimpleCanadaStorageSerializer(BaseCanadaStorageSerializer):
    root_collection_node_id: str = attr.ib()

    YT_DOCUMENT_DATA_KEY: ClassVar[str] = "data"
    YT_DOCUMENT_UNVERSIONED_DATA_KEY: ClassVar[str] = "unversioned_data"

    def _process_parent_id(self, parent_id: str) -> str | None:
        if parent_id == self.root_collection_node_id:
            return None
        return parent_id

    def serialize_collection(self, collection: Collection) -> SerializableEntity:
        return SerializableEntity(
            title=collection.title,
            node_type=yt_const.YTNodeType.map_node,
            data=None,
            attributes={
                yt_const.YTAttributes.DL_TYPE.value: CanadaEntityType.collection.value,
            },
        )

    def deserialize_collection(self, raw_data: dict) -> Collection:
        collection_id = raw_data[yt_const.YTAttributes.ID.value]

        return Collection(
            collection_id=collection_id,
            parent_id=self._process_parent_id(raw_data[yt_const.YTAttributes.PARENT_ID.value]),
            title=raw_data[yt_const.YTAttributes.KEY.value],
            modification_info=ModificationInfo(
                created_by=raw_data[yt_const.YTAttributes.OWNER.value],
                created_at=raw_data[yt_const.YTAttributes.CREATION_TIME.value],
                updated_by="unknown",
                updated_at=raw_data[yt_const.YTAttributes.MOD_TIME.value],
            ),
        )

    def serialize_workbook(self, workbook: Workbook) -> SerializableEntity:
        return SerializableEntity(
            title=workbook.title,
            node_type=yt_const.YTNodeType.map_node,
            data=None,
            attributes={
                yt_const.YTAttributes.DL_TYPE.value: CanadaEntityType.workbook.value,
            },
        )

    def deserialize_workbook(self, raw_data: dict) -> Workbook:
        return Workbook(
            workbook_id=raw_data[yt_const.YTAttributes.ID.value],
            collection_id=self._process_parent_id(raw_data[yt_const.YTAttributes.PARENT_ID.value]),
            title=raw_data[yt_const.YTAttributes.KEY.value],
            modification_info=ModificationInfo(
                created_by=raw_data[yt_const.YTAttributes.OWNER.value],
                created_at=raw_data[yt_const.YTAttributes.CREATION_TIME.value],
                updated_by="unknown",
                updated_at=raw_data[yt_const.YTAttributes.MOD_TIME.value],
            ),
        )

    def serialize_entry(self, entry: Entry) -> SerializableEntity:
        return SerializableEntity(
            title=entry.title,
            node_type=yt_const.YTNodeType.document,
            data={
                self.YT_DOCUMENT_DATA_KEY: entry.data,
                self.YT_DOCUMENT_UNVERSIONED_DATA_KEY: entry.unversioned_data,
            },
            attributes={
                yt_const.YTAttributes.DL_TYPE.value: CanadaEntityType.entry.value,
                yt_const.YTAttributes.DL_ENTRY_SCOPE.value: entry.scope,
                yt_const.YTAttributes.DL_ENTRY_TYPE.value: entry.entry_type,
            },
        )

    def deserialize_entry(self, raw_data: dict, attributes: dict[str, str]) -> Entry:
        return Entry(
            data=raw_data.get(self.YT_DOCUMENT_DATA_KEY, {}),
            unversioned_data=raw_data.get(self.YT_DOCUMENT_UNVERSIONED_DATA_KEY, {}),
            entry_id=attributes[yt_const.YTAttributes.ID.value],
            workbook_id=attributes[yt_const.YTAttributes.PARENT_ID.value],
            title=attributes[yt_const.YTAttributes.KEY.value],
            scope=attributes[yt_const.YTAttributes.DL_ENTRY_SCOPE.value],
            entry_type=attributes[yt_const.YTAttributes.DL_ENTRY_TYPE.value],
            meta={"state": "saved"},
            modification_info=ModificationInfo(
                created_by=attributes[yt_const.YTAttributes.OWNER.value],
                created_at=attributes[yt_const.YTAttributes.CREATION_TIME.value],
                updated_by="unknown",
                updated_at=attributes[yt_const.YTAttributes.MOD_TIME.value],
            ),
        )
