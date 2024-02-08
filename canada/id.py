from canada.settings import YT_HOME_PREFIX


class ID(str):
    @property
    def pseudo_path(self):
        return f"#{self}"


DELIMITER = "."


class ID_:
    def __init__(self, parts: list[str]):
        self._parts: list[str] = parts

    def __bool__(self):
        return len(self._parts) > 0

    def __str__(self):
        return self.to_str()

    def to_str(self):
        return DELIMITER.join(self._parts)

    def to_path(self) -> str:
        if not self._parts:
            return YT_HOME_PREFIX
        else:
            return YT_HOME_PREFIX + "/" + "/".join(self._parts)

    def get_parent(self):
        return ID(parts=self._parts[:-1])

    @classmethod
    def from_str(cls, _id: str | None):
        return cls(parts=_id.split(DELIMITER)) if _id is not None else cls(parts=[])

    def add(self, key: str):
        return ID(parts=self._parts + [key])

    @classmethod
    def empty(cls):
        return cls(parts=[])
