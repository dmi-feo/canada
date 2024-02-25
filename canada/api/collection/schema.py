import marshmallow as ma

from canada.api import base_schema
from canada.contrib.ma_top_level import TopLevelSchema


class RootCollectionPermissionsResponse(ma.Schema):
    createCollectionInRoot = ma.fields.Bool()
    createWorkbookInRoot = ma.fields.Bool()


class CollectionResponseSchema(base_schema.CollectionSchema):
    pass


class CollectionBreadcrumbsResponse(TopLevelSchema):
    class CollectionShortRepr(ma.Schema):
        collectionId = ma.fields.String()
        title = ma.fields.String()

    _toplevel = ma.fields.Nested(CollectionShortRepr(), many=True)


class CollectionContentResponseSchema(ma.Schema):
    collections = ma.fields.Nested(base_schema.CollectionSchema(), many=True)
    collectionsNextPageToken = ma.fields.String()
    workbooks = ma.fields.Nested(base_schema.WorkbookSchema(), many=True)
    workbooksNextPageToken = ma.fields.String()


class CreateCollectionRequest(ma.Schema):
    title = ma.fields.String()
    parentId = ma.fields.String(allow_none=True)
    description = ma.fields.String()


class CreateCollectionResponse(base_schema.CollectionSchema):
    pass


class DeleteCollectionResponse(ma.Schema):
    pass
