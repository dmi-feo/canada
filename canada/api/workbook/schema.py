import marshmallow as ma

from canada.api.base_schema import (
    EntrySchema,
    WorkbookSchema,
)


class CreateWorkbookRequest(ma.Schema):
    collectionId = ma.fields.String(allow_none=True)
    title = ma.fields.String()
    description = ma.fields.String()


class CreateWorkbookResponse(WorkbookSchema):
    pass


class GetWorkbookResponse(WorkbookSchema):
    pass


class GetWorkbookEntriesResponse(ma.Schema):
    entries = ma.fields.Nested(EntrySchema(), many=True)


class DeleteWorkbookResponse(ma.Schema):
    pass
