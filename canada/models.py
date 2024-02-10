from dataclasses import dataclass


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
    collection_id: str
    parent_id: str | None
    permissions: CollectionPermissions


@dataclass
class Workbook(BaseUSContainer):
    workbook_id: str
    collection_id: str  # like `parentId` for collections, so not in the base class
    permissions: Permissions


@dataclass
class CollectionContent:
    collections: list[Collection]
    workbooks: list[Workbook]


@dataclass
class Entry(BaseUSEntity):
    data: dict
    unversioned_data: dict
    entry_id: str
    workbook_id: str
    key: str  # TODO: really required?
    permissions: dict  # TODO: really required? then make a dataclass
    published_id: str | None
    rev_id: str | None
    saved_id: str | None
    scope: str
    entry_type: str
    hidden: bool
