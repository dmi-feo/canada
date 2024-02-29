from __future__ import annotations

import abc
from typing import TYPE_CHECKING

import attr

from canada.models import Workbook, Collection, Entry

if TYPE_CHECKING:
    from canada.entity_alias_manager import BaseEntityAliasManager


class BaseCanadaApiSerializer(abc.ABC):
    @abc.abstractmethod
    def _resolve_entity_alias(self, alias: str) -> str:
        pass

    @abc.abstractmethod
    def serialize_collection(self, collection: Collection) -> dict:
        pass

    @abc.abstractmethod
    def deserialize_collection(self, raw_data: dict) -> Collection:
        pass

    @abc.abstractmethod
    def serialize_workbook(self, workbook: Workbook) -> dict:
        pass

    @abc.abstractmethod
    def deserialize_workbook(self, raw_data: dict) -> Workbook:
        pass

    @abc.abstractmethod
    def serialize_entry(self, entry: Entry) -> dict:
        pass

    @abc.abstractmethod
    def deserialize_entry(self, raw_data: dict) -> Entry:
        pass


@attr.s
class SimpleCanadaApiSerializer(BaseCanadaApiSerializer):
    entity_alias_manager: BaseEntityAliasManager = attr.ib()

    def _resolve_entity_alias(self, alias: str) -> str:
        return self.entity_alias_manager.resolve_alias(alias)

    def serialize_collection(self, collection: Collection) -> dict:
        return {
            "collectionId": collection.collection_id,
            "parentId": collection.parent_id,
            "title": collection.title,
            "description": collection.description,
            "meta": {},
            "createdBy": collection.modification_info.created_by,
            "createdAt": collection.modification_info.created_at,
            "updatedBy": collection.modification_info.updated_by,
            "updatedAt": collection.modification_info.updated_at,
            "tenantId": "common",
            "projectId": None,
            "permissions": {
                "createCollection": True,
                "createWorkbook": True,
                "listAccessBindings": True,
                "updateAccessBindings": True,
                "limitedView": True,
                "view": True,
                "update": True,
                "copy": True,
                "move": True,
                "publish": True,
                "embed": True,
                "delete": True,
            },
        }

    def deserialize_collection(self, raw_data: dict) -> Collection:
        return Collection(
            collection_id=None,
            parent_id=self._resolve_entity_alias(raw_data["parentId"]),
            title=raw_data["title"],
            description=raw_data["description"],
        )

    def serialize_workbook(self, workbook: Workbook) -> dict:
        return {
            "workbookId": workbook.workbook_id,
            "collectionId": workbook.collection_id,
            "title": workbook.title,
            "description": workbook.description,
            "meta": {},
            "createdBy": workbook.modification_info.created_by,
            "createdAt": workbook.modification_info.created_at,
            "updatedBy": workbook.modification_info.updated_by,
            "updatedAt": workbook.modification_info.updated_at,
            "tenantId": "common",
            "projectId": None,
            "permissions": {
                "listAccessBindings": True,
                "updateAccessBindings": True,
                "limitedView": True,
                "view": True,
                "update": True,
                "copy": True,
                "move": True,
                "publish": True,
                "embed": True,
                "delete": True,
            },
        }

    def deserialize_workbook(self, raw_data: dict) -> Workbook:
        return Workbook(
            workbook_id=None,
            collection_id=self._resolve_entity_alias(raw_data["collectionId"]),
            title=raw_data["title"],
            description=raw_data["description"],
        )

    def serialize_entry(self, entry: Entry) -> dict:
        return {
            "entryId": entry.entry_id,
            "workbookId": entry.workbook_id,
            "data": entry.data,
            "unversionedData": entry.unversioned_data,
            "key": entry.title,
            "scope": entry.scope,
            "type": entry.entry_type,
            "meta": {},
            "createdBy": entry.modification_info.created_by,
            "createdAt": entry.modification_info.created_at,
            "updatedBy": entry.modification_info.updated_by,
            "updatedAt": entry.modification_info.updated_at,
            "tenantId": "common",
            "publishedId": None,
            "revId": None,
            "savedId": None,
            "hidden": False,
            "permissions": {
                "admin": True,
                "edit": True,
                "read": True,
                "execute": True,
            },
        }

    def deserialize_entry(self, raw_data: dict) -> Entry:
        return Entry(
            entry_id=None,
            workbook_id=self._resolve_entity_alias(raw_data["workbookId"]),
            data=raw_data["data"],
            unversioned_data=raw_data.get("unversionedData", {}),
            title=raw_data["name"],
            scope=raw_data["scope"],
            entry_type=raw_data["type"],
        )
