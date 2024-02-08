YT_ATTR_DL_TYPE = "dl_type"
YT_ATTR_DL_TITLE = "dl_title"
YT_ATTR_DL_DESCRIPTION = "dl_description"
YT_ATTR_DL_ENTRY_TYPE = "dl_entry_type"
YT_ATTR_DL_ENTRY_SCOPE = "dl_entry_scope"
YT_ATTR_ID = "id"

YT_ATTR_DL_ALL = [
    YT_ATTR_DL_TYPE, YT_ATTR_DL_TITLE, YT_ATTR_DL_DESCRIPTION,
    YT_ATTR_DL_ENTRY_TYPE, YT_ATTR_DL_ENTRY_SCOPE
]

YT_ATTRS_TO_REQ = [
    *YT_ATTR_DL_ALL,
    "creation_time",
    "modification_time",
    YT_ATTR_ID,
]

DL_COLLECTION_TYPE = "collection"
DL_WORKBOOK_TYPE = "workbook"
DL_ENTRY_TYPE = "entry"
