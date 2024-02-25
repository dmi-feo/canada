import marshmallow as ma


class BaseUSEntitySchema(ma.Schema):
    meta = ma.fields.Dict()
    createdBy = ma.fields.String()
    createdAt = ma.fields.String()
    updatedBy = ma.fields.String()
    updatedAt = ma.fields.String()
    tenantId = ma.fields.String()


class BaseUSContainerSchema(BaseUSEntitySchema):
    title = ma.fields.String()
    description = ma.fields.String()
    parentId = ma.fields.String()
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
    collectionId = ma.fields.String()
    permissions = ma.fields.Nested(CollectionPermissionsSchema())


class WorkbookSchema(BaseUSContainerSchema):
    workbookId = ma.fields.String()
    collectionId = ma.fields.String()
    permissions = ma.fields.Nested(BasePermissionsSchema())


class EntrySchema(BaseUSEntitySchema):
    class EntryPermissions(ma.Schema):
        admin = ma.fields.Bool()
        edit = ma.fields.Bool()
        read = ma.fields.Bool()
        execute = ma.fields.Bool()

    data = ma.fields.Dict()
    unversionedData = ma.fields.Dict()
    entryId = ma.fields.String()
    key = ma.fields.String()
    permissions = ma.fields.Nested(EntryPermissions())
    publishedId = ma.fields.String()
    revId = ma.fields.String()
    savedId = ma.fields.String()
    scope = ma.fields.String()
    type = ma.fields.String()
    workbookId = ma.fields.String()
    hidden = ma.fields.Bool()
