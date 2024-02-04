import marshmallow as ma

from canada import base_schema, base_schema as bsch
from canada.contrib.ma_top_level import TopLevelSchema


class RootCollectionPermissionsResponse(ma.Schema):
    create_collection_in_root = ma.fields.Bool(data_key="createCollectionInRoot")
    create_workbook_in_root = ma.fields.Bool(data_key="createWorkbookInRoot")


class CollectionResponseSchema(base_schema.CollectionSchema):
    pass


class InternalObject(ma.Schema):
    collection_id = base_schema.IDField(data_key="collectionId")
    title = ma.fields.String()


class CollectionBreadcrumbsResponse(TopLevelSchema):
    _toplevel = ma.fields.Nested(InternalObject, many=True)


class CollectionContentResponseSchema(ma.Schema):
    collections = ma.fields.Nested(bsch.CollectionSchema, many=True)
    collections_next_page_token = ma.fields.Bool(data_key="collectionsNextPageToken")
    workbooks = ma.fields.Nested(bsch.WorkbookSchema, many=True)
    workbooks_next_page_token = ma.fields.Bool(data_key="workbooksNextPageToken")


class CreateCollectionRequest(ma.Schema):
    title = ma.fields.String()
    parent_id = base_schema.IDField(allow_none=True, data_key="parentId")
    description = ma.fields.String()


class CreateCollectionResponse(base_schema.CollectionSchema):
    pass
