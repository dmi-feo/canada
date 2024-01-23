import marshmallow as ma

from canada import base_schema, base_schema as bsch
from canada.contrib.ma_top_level import TopLevelSchema


class RootCollectionPermissionsResponse(ma.Schema):
    createCollectionInRoot = ma.fields.Bool()
    createWorkbookInRoot = ma.fields.Bool()


class CollectionResponseSchema(base_schema.CollectionSchema):
    pass


class InternalObject(ma.Schema):
    collectionId = base_schema.IDField()
    title = ma.fields.String()


class CollectionBreadcrumbsResponse(TopLevelSchema):
    _toplevel = ma.fields.Nested(InternalObject, many=True)


class CollectionContentResponseSchema(ma.Schema):
    collections = ma.fields.Nested(bsch.CollectionSchema, many=True)
    collectionsNextPageToken = ma.fields.Bool()
    workbooks = ma.fields.Nested(bsch.WorkbookSchema, many=True)
    workbooksNextPageToken = ma.fields.Bool()


class CreateCollectionRequest(ma.Schema):
    title = ma.fields.String()
    parentId = base_schema.IDField(allow_none=True)
    description = ma.fields.String()


class CreateCollectionResponse(base_schema.CollectionSchema):
    pass
