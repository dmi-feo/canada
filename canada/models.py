from typing import Any

import attr


@attr.s
class ModificationInfo:
    created_by: str | None = attr.ib(default=None)
    created_at: str | None = attr.ib(default=None)
    updated_by: str | None = attr.ib(default=None)
    updated_at: str | None = attr.ib(default=None)


@attr.s
class Collection:
    collection_id: str | None = attr.ib()
    parent_id: str | None = attr.ib()
    title: str = attr.ib()
    description: str = attr.ib(default="")
    meta: dict = attr.ib(factory=dict)
    modification_info: ModificationInfo = attr.ib(default=ModificationInfo())


@attr.s
class Workbook:
    workbook_id: str | None = attr.ib()
    collection_id: str | None = attr.ib()
    title: str = attr.ib()
    description: str = attr.ib(default="")
    meta: dict = attr.ib(factory=dict)
    modification_info: ModificationInfo = attr.ib(default=ModificationInfo())


@attr.s
class Entry:
    entry_id: str | None = attr.ib()
    data: dict = attr.ib()
    unversioned_data: dict = attr.ib()
    workbook_id: str = attr.ib()
    title: str = attr.ib()
    scope: str = attr.ib()
    entry_type: str = attr.ib()
    meta: dict = attr.ib(factory=dict)
    modification_info: ModificationInfo = attr.ib(default=ModificationInfo())


@attr.s
class CollectionContent:  # TODO: should be handled by api schema?
    collections: list[Collection] = attr.ib()
    workbooks: list[Workbook] = attr.ib()
