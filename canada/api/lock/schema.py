import marshmallow as ma


class CreateLockRequest(ma.Schema):
    duration = ma.fields.Int(allow_none=True)
    force = ma.fields.Bool(allow_none=True)  # TODO: implement


class CreateLockResponse(ma.Schema):
    lockToken = ma.fields.String()


class DeleteLockResponse(ma.Schema):
    pass
