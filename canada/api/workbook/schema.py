import marshmallow as ma

from canada.base_schema import WorkbookSchema, EntrySchema


class CreateWorkbookRequest(ma.Schema):
    collectionId = ma.fields.String()
    title = ma.fields.String()
    description = ma.fields.String()


class CreateWorkbookResponse(WorkbookSchema):
    pass


class GetWorkbookResponse(WorkbookSchema):
    pass


class GetWorkbookEntriesResponse(ma.Schema):
    entries = ma.fields.Nested(EntrySchema(), many=True)
