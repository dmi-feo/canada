import marshmallow as ma

from canada.base_schema import IDField, WorkbookSchema


class CreateWorkbookRequest(ma.Schema):
    collectionId = IDField()
    title = ma.fields.String()
    description = ma.fields.String()


class CreateWorkbookResponse(WorkbookSchema):
    pass


class GetWorkbookResponse(WorkbookSchema):
    pass
