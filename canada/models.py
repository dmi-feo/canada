from dataclasses import dataclass

from canada.id import ID


@dataclass
class Permissions:
    list_access_bindings: bool
    update_access_bindings: bool
    limited_view: bool
    view: bool
    update: bool
    copy: bool
    move: bool
    publish: bool
    embed: bool
    delete: bool


@dataclass
class BaseUSEntity:
    tenant_id: str | None
    meta: dict
    created_by: str
    created_at: str
    updated_by: str
    updated_at: str


@dataclass
class BaseUSContainer(BaseUSEntity):
    title: str
    description: str
    project_id: str | None


@dataclass
class CollectionPermissions(Permissions):
    create_collection: bool
    create_workbook: bool


@dataclass
class Collection(BaseUSContainer):
    collection_id: ID
    parent_id: ID | None
    permissions: CollectionPermissions


@dataclass
class Workbook(BaseUSContainer):
    workbook_id: ID
    collection_id: ID  # like `parentId` for collections, so not in the base class
    permissions: Permissions


@dataclass
class CollectionContent:
    collections: list[Collection]
    workbooks: list[Workbook]


@dataclass
class Entry(BaseUSEntity):
    data: dict
    unversioned_data: dict
    entry_id: ID
    workbook_id: ID
    key: str  # TODO: really required?
    permissions: dict  # TODO: really required? then make a dataclass
    published_id: ID
    rev_id: ID
    saved_id: ID
    scope: str
    entry_type: str
    hidden: bool
