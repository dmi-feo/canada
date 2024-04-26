from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
    ClassVar,
)

import attr

from canada.constants import CanadaEntityType
from canada.models import (
    Collection,
    Entry,
    ModificationInfo,
    Workbook,
)
from canada.yt_wb_manager import constants as yt_const


if TYPE_CHECKING:
    from canada.types import JSONDict


@attr.s
class SerializableEntity:
    title: str = attr.ib()
    attributes: dict[str, str] = attr.ib()
    data: JSONDict | None = attr.ib(default=None)


class BaseCanadaStorageSerializer(ABC):
    @abstractmethod
    def serialize_collection(self, collection: Collection) -> SerializableEntity:
        pass

    @abstractmethod
    def deserialize_collection(self, raw_data: SerializableEntity) -> Collection:
        pass

    @abstractmethod
    def serialize_workbook(self, workbook: Workbook) -> SerializableEntity:
        pass

    @abstractmethod
    def deserialize_workbook(self, raw_data: SerializableEntity) -> Workbook:
        pass

    @abstractmethod
    def serialize_entry(self, entry: Entry) -> SerializableEntity:
        pass

    @abstractmethod
    def deserialize_entry(self, raw_data: SerializableEntity) -> Entry:
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
            data=None,
            attributes={
                yt_const.YTAttributes.DL_TYPE.value: CanadaEntityType.collection.value,
            },
        )

    def deserialize_collection(self, raw_data: SerializableEntity) -> Collection:
        collection_id = raw_data.attributes[yt_const.YTAttributes.ID.value]

        return Collection(
            collection_id=collection_id,
            parent_id=self._process_parent_id(raw_data.attributes[yt_const.YTAttributes.PARENT_ID.value]),
            title=raw_data.title,
            modification_info=ModificationInfo(
                created_by=raw_data.attributes[yt_const.YTAttributes.OWNER.value],
                created_at=raw_data.attributes[yt_const.YTAttributes.CREATION_TIME.value],
                updated_by="unknown",
                updated_at=raw_data.attributes[yt_const.YTAttributes.MOD_TIME.value],
            ),
        )

    def serialize_workbook(self, workbook: Workbook) -> SerializableEntity:
        return SerializableEntity(
            title=workbook.title,
            data=None,
            attributes={
                yt_const.YTAttributes.DL_TYPE.value: CanadaEntityType.workbook.value,
            },
        )

    def deserialize_workbook(self, raw_data: SerializableEntity) -> Workbook:
        return Workbook(
            workbook_id=raw_data.attributes[yt_const.YTAttributes.ID.value],
            collection_id=self._process_parent_id(raw_data.attributes[yt_const.YTAttributes.PARENT_ID.value]),
            title=raw_data.title,
            modification_info=ModificationInfo(
                created_by=raw_data.attributes[yt_const.YTAttributes.OWNER.value],
                created_at=raw_data.attributes[yt_const.YTAttributes.CREATION_TIME.value],
                updated_by="unknown",
                updated_at=raw_data.attributes[yt_const.YTAttributes.MOD_TIME.value],
            ),
        )

    def serialize_entry(self, entry: Entry) -> SerializableEntity:
        return SerializableEntity(
            title=entry.title,
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

    def deserialize_entry(self, raw_data: SerializableEntity) -> Entry:
        return Entry(
            data=(raw_data.data[self.YT_DOCUMENT_DATA_KEY] if raw_data.data is not None else {}),
            unversioned_data=(
                raw_data.data[self.YT_DOCUMENT_UNVERSIONED_DATA_KEY] if raw_data.data is not None else {}
            ),
            entry_id=raw_data.attributes[yt_const.YTAttributes.ID.value],
            workbook_id=raw_data.attributes[yt_const.YTAttributes.PARENT_ID.value],
            title=raw_data.title,
            scope=raw_data.attributes[yt_const.YTAttributes.DL_ENTRY_SCOPE.value],
            entry_type=raw_data.attributes[yt_const.YTAttributes.DL_ENTRY_TYPE.value],
            meta={"state": "saved"},
            modification_info=ModificationInfo(
                created_by=raw_data.attributes[yt_const.YTAttributes.OWNER.value],
                created_at=raw_data.attributes[yt_const.YTAttributes.CREATION_TIME.value],
                updated_by="unknown",
                updated_at=raw_data.attributes[yt_const.YTAttributes.MOD_TIME.value],
            ),
        )
