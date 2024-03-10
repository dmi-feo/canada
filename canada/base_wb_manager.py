from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from canada.models import CollectionContent, Workbook, Collection, Entry

if TYPE_CHECKING:
    from canada.types import JSONDict


class BaseWorkbookManager(abc.ABC):
    @abc.abstractmethod
    async def list_collection(self, coll_id: str | None = None) -> CollectionContent:
        pass

    @abc.abstractmethod
    async def get_collection(self, coll_id: str) -> Collection:
        pass

    @abc.abstractmethod
    async def create_collection(self, collection: Collection) -> str:
        pass

    @abc.abstractmethod
    async def delete_collection(self, coll_id: str) -> None:
        pass

    @abc.abstractmethod
    async def get_workbook(self, wb_id: str) -> Workbook:
        pass

    @abc.abstractmethod
    async def create_workbook(self, workbook: Workbook) -> str:
        pass

    @abc.abstractmethod
    async def get_workbook_entries(self, wb_id: str, scope: str | None) -> list[Entry]:
        pass

    @abc.abstractmethod
    async def delete_workbook(self, wb_id: str) -> None:
        pass

    @abc.abstractmethod
    async def get_entry(self, entry_id: str) -> Entry:
        pass

    @abc.abstractmethod
    async def create_entry(self, entry: Entry) -> str:
        pass

    @abc.abstractmethod
    async def update_entry(
            self, entry_id: str,
            entry_data: JSONDict | None, unversioned_data: JSONDict | None,
            lock_token: str | None = None,
    ) -> None:
        # TODO: introduce EntryUpdate object
        pass

    @abc.abstractmethod
    async def delete_entry(self, entry_id: str) -> None:
        pass

    @abc.abstractmethod
    async def set_lock(self, entry_id: str, duration: int | None = None, force: bool | None = None) -> str:
        pass

    @abc.abstractmethod
    async def delete_lock(self, entry_id: str, lock_id: str) -> None:
        pass
