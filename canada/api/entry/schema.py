import marshmallow as ma

from canada.base_schema import EntrySchema


class GetEntryResponse(EntrySchema):
    pass


class CreateEntryRequest(ma.Schema):
    name = ma.fields.String()
    data = ma.fields.Dict()
    unversioned_data = ma.fields.Dict(data_key="unversionedData", load_default=dict)
    mode = ma.fields.String()
    meta = ma.fields.Dict()
    workbook_id = ma.fields.String(data_key="workbookId")
    type = ma.fields.String()
    scope = ma.fields.String()
    recursion = ma.fields.Bool()
    links = ma.fields.Dict()
    hidden = ma.fields.Bool()
    # no idea why, but wizard requires it
    include_permission_info = ma.fields.Bool(data_key="includePermissionsInfo", load_default=None)


class CreateEntryResponse(ma.Schema):
    entry_id = ma.fields.String(data_key="entryId")


class UpdateEntryRequest(ma.Schema):
    data = ma.fields.Dict(load_default=None)
    unversioned_data = ma.fields.Dict(data_key="unversionedData", load_default=None)
    mode = ma.fields.String()
    meta = ma.fields.Dict()
    links = ma.fields.Dict()


class UpdateEntryResponse(ma.Schema):
    entry_id = ma.fields.String(data_key="entryId")


class GetEntryMeta(ma.Schema):
    pass  # no idea what should be returned - apparently it doesn't matter at all
