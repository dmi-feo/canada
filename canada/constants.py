import enum


class CanadaEntityType(enum.Enum):
    collection = "collection"
    workbook = "workbook"
    entry = "entry"


class WellKnownIDMode(enum.Enum):
    disabled = "disabled"
    from_file = "from_file"
