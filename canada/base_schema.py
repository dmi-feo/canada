import marshmallow as ma


class IDField(ma.fields.String):
    pass


class BaseUSEntitySchema(ma.Schema):
    meta = ma.fields.Dict()
    created_by = ma.fields.String(data_key="createdBy")  # TODO: consider datetime
    created_at = ma.fields.String(data_key="createdAt")
    updated_by = ma.fields.String(data_key="updatedBy")
    updated_at = ma.fields.String(data_key="updatedAt")
    tenant_id = ma.fields.String(data_key="tenantId")


class BaseUSContainerSchema(BaseUSEntitySchema):
    title = ma.fields.String()
    description = ma.fields.String()
    parent_id = IDField(data_key="parentId")
    project_id = ma.fields.String(data_key="projectId")


class BasePermissionsSchema(ma.Schema):
    list_access_bindings = ma.fields.Bool(data_key="listAccessBindings")
    update_access_bindings = ma.fields.Bool(data_key="updateAccessBindings")
    limited_view = ma.fields.Bool(data_key="limitedView")
    view = ma.fields.Bool()
    update = ma.fields.Bool()
    copy = ma.fields.Bool()
    move = ma.fields.Bool()
    publish = ma.fields.Bool()
    embed = ma.fields.Bool()
    delete = ma.fields.Bool()


class CollectionPermissionsSchema(BasePermissionsSchema):
    create_collection = ma.fields.Bool(data_key="createCollection")
    create_workbook = ma.fields.Bool(data_key="createWorkbook")


class CollectionSchema(BaseUSContainerSchema):
    collection_id = IDField(data_key="collectionId")
    parent_id = IDField(data_key="parent_id")
    permissions = ma.fields.Nested(CollectionPermissionsSchema)


class WorkbookSchema(BaseUSContainerSchema):
    workbook_id = IDField(data_key="workbookId")
    collection_id = IDField(data_key="collectionId")  # like `parentId` for collections, so not in the base class
    permissions = ma.fields.Nested(BasePermissionsSchema)


class EntrySchema(BaseUSEntitySchema):
    class EntryPermissions(ma.Schema):
        admin = ma.fields.Bool()
        edit = ma.fields.Bool()
        read = ma.fields.Bool()
        execute = ma.fields.Bool()

    data = ma.fields.Dict()
    unversioned_data = ma.fields.Dict(data_key="unversionedData")
    entry_id = ma.fields.String(data_key="entryId")
    key = ma.fields.String()
    permissions = ma.fields.Nested(EntryPermissions())
    published_id = ma.fields.String(data_key="publishedId")
    rev_id = ma.fields.String(data_key="revId")
    saved_id = ma.fields.String(data_key="savedId")
    scope = ma.fields.String()
    entry_type = ma.fields.String(data_key="type")
    workbook_id = ma.fields.String(data_key="workbookId")
    hidden = ma.fields.Bool()
