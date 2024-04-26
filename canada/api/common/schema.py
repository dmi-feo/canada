import marshmallow as ma


class PingResponse(ma.Schema):
    msg = ma.fields.String()
