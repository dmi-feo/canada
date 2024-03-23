import attr


class BaseWBManagerError(Exception):
    pass


@attr.s
class WBManagerStorageError(BaseWBManagerError):
    message: str = attr.ib()
