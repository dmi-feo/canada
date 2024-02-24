import marshmallow as ma

from canada.base_schema import EntrySchema


class GetEntryResponse(EntrySchema):
    pass


class CreateEntryRequest(ma.Schema):
    name = ma.fields.String()
    data = ma.fields.Dict()
    unversionedData = ma.fields.Dict()
    mode = ma.fields.String()
    meta = ma.fields.Dict()
    workbookId = ma.fields.String()
    type = ma.fields.String()
    scope = ma.fields.String()
    recursion = ma.fields.Bool()
    links = ma.fields.Dict()
    hidden = ma.fields.Bool()
    # no idea why, but wizard requires it
    includePermissionsInfo = ma.fields.Bool()


class CreateEntryResponse(ma.Schema):
    entryId = ma.fields.String()


class UpdateEntryRequest(ma.Schema):
    data = ma.fields.Dict()
    unversionedData = ma.fields.Dict()
    mode = ma.fields.String()
    meta = ma.fields.Dict()
    links = ma.fields.Dict()


class UpdateEntryResponse(ma.Schema):
    entryId = ma.fields.String()


class GetEntryMeta(ma.Schema):
    # no idea what should be returned - apparently it doesn't matter at all
    # https://github.com/datalens-tech/datalens-ui/commit/80238ac7145f3684180a9177f86f66550d12f457#diff-ff70a027a67830c9bc9b102debb7b6f657a72d5101040edeec8636d90247d263R212
    pass
