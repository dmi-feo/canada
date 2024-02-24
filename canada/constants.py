import enum
from enum import Enum


YT_ATTR_DL_TYPE = "dl_type"
YT_ATTR_DL_ENTRY_TYPE = "dl_entry_type"
YT_ATTR_DL_ENTRY_SCOPE = "dl_entry_scope"
YT_ATTR_ID = "id"
YT_ATTR_PARENT_ID = "parent_id"
YT_ATTR_CREATION_TIME = "creation_time"
YT_ATTR_MOD_TIME = "modification_time"
YT_ATTR_OWNER = "owner"
YT_ATTR_TYPE = "type"
YT_ATTR_KEY = "key"

YT_LIST_ATTRS_KEY = "$attributes"

YT_ATTR_DL_ALL = [
    YT_ATTR_DL_TYPE,
    YT_ATTR_DL_ENTRY_TYPE,
    YT_ATTR_DL_ENTRY_SCOPE,
]

YT_ATTRS_TO_REQ = [
    *YT_ATTR_DL_ALL,
    YT_ATTR_CREATION_TIME,
    YT_ATTR_MOD_TIME,
    YT_ATTR_ID,
    YT_ATTR_PARENT_ID,
    YT_ATTR_OWNER,
    YT_ATTR_TYPE,
    YT_ATTR_KEY,
]

YT_COOKIE_TOKEN_NAME = "YTCypressCookie"
YT_HEADER_CSRF_NAME = "X-Csrf-Token"

DL_COLLECTION_TYPE = "collection"
DL_WORKBOOK_TYPE = "workbook"
DL_ENTRY_TYPE = "entry"


class YTNodeType(enum.Enum):
    map_node = "map_node"
    document = "document"


class CanadaEntityType(enum.Enum):
    collection = "collection"
    workbook = "workbook"
    entry = "entry"
