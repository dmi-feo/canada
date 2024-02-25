import enum


class YTAttributes(enum.Enum):
    DL_TYPE = "dl_type"
    DL_ENTRY_TYPE = "dl_entry_type"
    DL_ENTRY_SCOPE = "dl_entry_scope"
    ID = "id"
    PARENT_ID = "parent_id"
    CREATION_TIME = "creation_time"
    MOD_TIME = "modification_time"
    OWNER = "owner"
    TYPE = "type"
    KEY = "key"


YT_LIST_ATTRIBUTES_KEY = "$attributes"

YT_ATTR_DL_ALL = [
    YTAttributes.DL_TYPE,
    YTAttributes.DL_ENTRY_TYPE,
    YTAttributes.DL_ENTRY_SCOPE,
]

YT_ATTRS_TO_REQ = [
    *[at.value for at in YT_ATTR_DL_ALL],
    YTAttributes.CREATION_TIME.value,
    YTAttributes.MOD_TIME.value,
    YTAttributes.ID.value,
    YTAttributes.PARENT_ID.value,
    YTAttributes.OWNER.value,
    YTAttributes.TYPE.value,
    YTAttributes.KEY.value,
]

YT_COOKIE_TOKEN_NAME = "YTCypressCookie"
YT_HEADER_CSRF_NAME = "X-Csrf-Token"


class YTNodeType(enum.Enum):
    map_node = "map_node"
    document = "document"
    file = "file"


class YTAuthMode(enum.Enum):
    disabled = "disabled"
    pass_request_creds = "pass_request_creds"
    cookie_from_env = "from_env"


class YTLockMode(enum.Enum):
    snapshot = "snapshot"
    shared = "shared"
    exclusive = "exclusive"
