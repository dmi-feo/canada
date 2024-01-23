from dataclasses import dataclass

from canada.id import ID


@dataclass
class Permissions:
    listAccessBindings: bool
    updateAccessBindings: bool
    limitedView: bool
    view: bool
    update: bool
    copy: bool
    move: bool
    publish: bool
    embed: bool
    delete: bool


@dataclass
class BaseUSContainer:
    title: str
    description: str
    projectId: str | None
    tenantId: str | None
    meta: dict
    createdBy: str
    createdAt: str
    updatedBy: str
    updatedAt: str


@dataclass
class CollectionPermissions(Permissions):
    createCollection: bool
    createWorkbook: bool


@dataclass
class Collection(BaseUSContainer):
    collectionId: ID
    parentId: ID | None
    permissions: CollectionPermissions


@dataclass
class Workbook(BaseUSContainer):
    workbookId: ID
    collectionId: ID  # like `parentId` for collections, so not in the base class
    permissions: Permissions


@dataclass
class CollectionContent:
    collections: list[Collection]
    workbooks: list[Workbook]
