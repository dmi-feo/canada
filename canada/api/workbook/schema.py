import marshmallow as ma

from canada.base_schema import WorkbookSchema, EntrySchema


class CreateWorkbookRequest(ma.Schema):
    collection_id = ma.fields.String(data_key="collectionId")
    title = ma.fields.String()
    description = ma.fields.String()


class CreateWorkbookResponse(WorkbookSchema):
    pass


class GetWorkbookResponse(WorkbookSchema):
    pass


class GetWorkbookEntriesResponse(ma.Schema):
    entries = ma.fields.Nested(EntrySchema(), many=True)
