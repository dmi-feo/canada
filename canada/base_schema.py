import marshmallow as ma


class IDField(ma.fields.String):
    pass


class BaseUSEntitySchema(ma.Schema):
    meta = ma.fields.Dict()
    createdBy = ma.fields.String()  # TODO: consider datetime
    createdAt = ma.fields.String()
    updatedBy = ma.fields.String()
    updatedAt = ma.fields.String()
    tenantId = ma.fields.String()


class BaseUSContainerSchema(BaseUSEntitySchema):
    title = ma.fields.String()
    description = ma.fields.String()
    parentId = IDField()
    projectId = ma.fields.String()


class BasePermissionsSchema(ma.Schema):
    listAccessBindings = ma.fields.Bool()
    updateAccessBindings = ma.fields.Bool()
    limitedView = ma.fields.Bool()
    view = ma.fields.Bool()
    update = ma.fields.Bool()
    copy = ma.fields.Bool()
    move = ma.fields.Bool()
    publish = ma.fields.Bool()
    embed = ma.fields.Bool()
    delete = ma.fields.Bool()


class CollectionPermissionsSchema(BasePermissionsSchema):
    createCollection = ma.fields.Bool()
    createWorkbook = ma.fields.Bool()


class CollectionSchema(BaseUSContainerSchema):
    collectionId = IDField()
    parentId = IDField()
    permissions = ma.fields.Nested(CollectionPermissionsSchema)


class WorkbookSchema(BaseUSContainerSchema):
    workbookId = IDField()
    collectionId = IDField()  # like `parentId` for collections, so not in the base class
    permissions = ma.fields.Nested(BasePermissionsSchema)


class EntrySchema(BaseUSEntitySchema):
    data = ma.fields.Dict()
    entry_id = ma.fields.String(data_key="entryId")
    key = ma.fields.String()
    permissions = ma.fields.Dict()
    published_id = ma.fields.String(data_key="publishedId")
    rev_id = ma.fields.String(data_key="revId")
    saved_id = ma.fields.String(data_key="savedId")
    scope = ma.fields.String()
    type_ = ma.fields.String(data_key="type")
    workbook_id = ma.fields.String(data_key="workbookId")
