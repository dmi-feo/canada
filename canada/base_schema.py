import marshmallow as ma


class IDField(ma.fields.String):
    pass


class BaseUSContainerSchema(ma.Schema):
    title = ma.fields.String()
    description = ma.fields.String()
    parentId = IDField()
    projectId = ma.fields.String()
    tenantId = ma.fields.String()
    meta = ma.fields.Dict()
    createdBy = ma.fields.String()  # TODO: consider datetime
    createdAt = ma.fields.String()
    updatedBy = ma.fields.String()
    updatedAt = ma.fields.String()


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
