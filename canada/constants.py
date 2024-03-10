import enum


class CanadaEntityType(enum.Enum):
    collection = "collection"
    workbook = "workbook"
    entry = "entry"


class EntityAliasMode(enum.Enum):
    disabled = "disabled"
    from_file = "from_file"
    from_env = "from_env"


REQUEST_KEY_APP_SERVICES = "app_services"
