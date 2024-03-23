import attr


class BaseYtError(Exception):
    pass


@attr.s
class YtServerError(BaseYtError):
    message: str = attr.ib()
