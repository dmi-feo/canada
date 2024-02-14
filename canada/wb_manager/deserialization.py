from canada import constants as const
from canada.models import Workbook, Permissions, Collection, CollectionPermissions, Entry


def deserialize_workbook(raw_data: dict) -> Workbook:
    return Workbook(
        workbook_id=raw_data[const.YT_ATTR_ID],
        collection_id=raw_data[const.YT_ATTR_PARENT_ID],
        title=raw_data[const.YT_ATTR_KEY],
        description="",
        project_id=None,
        tenant_id=None,
        meta={},
        created_by=raw_data[const.YT_ATTR_OWNER],
        created_at=raw_data["creation_time"],
        updated_by="unknown",
        updated_at=raw_data["modification_time"],
        permissions=Permissions(
            list_access_bindings=True,
            update_access_bindings=True,
            limited_view=True,
            view=True,
            update=True,
            copy=True,
            move=True,
            publish=True,
            embed=True,
            delete=True,
        )
    )


def deserialize_collection(raw_data: dict) -> Collection:
    collection_id = raw_data[const.YT_ATTR_ID]

    return Collection(
        collection_id=collection_id,
        parent_id=raw_data[const.YT_ATTR_PARENT_ID],
        title=raw_data[const.YT_ATTR_KEY],
        description="",
        project_id=None,
        tenant_id=None,
        meta={},
        created_by=raw_data[const.YT_ATTR_OWNER],
        created_at=raw_data["creation_time"],
        updated_by="unknown",
        updated_at=raw_data["modification_time"],
        permissions=CollectionPermissions(
            list_access_bindings=True,
            update_access_bindings=True,
            limited_view=True,
            view=True,
            update=True,
            copy=True,
            move=True,
            publish=True,
            embed=True,
            delete=True,
            create_collection=True,
            create_workbook=True,
        )
    )


def deserialize_entry(raw_data: dict, attributes: dict[str, str]) -> Entry:
    return Entry(
        data=raw_data.get("data", {}),
        unversioned_data=raw_data.get("unversioned_data", {}),
        entry_id=attributes[const.YT_ATTR_ID],
        workbook_id=attributes[const.YT_ATTR_PARENT_ID],
        key=attributes[const.YT_ATTR_KEY],
        permissions={"admin": True, "edit": True, "read": True, "execute": True},
        published_id=None,
        rev_id=None,
        saved_id=None,
        scope=attributes[const.YT_ATTR_DL_ENTRY_SCOPE],
        entry_type=attributes[const.YT_ATTR_DL_ENTRY_TYPE],
        tenant_id=None,
        meta={"state": "saved"},
        created_by=attributes[const.YT_ATTR_OWNER],
        created_at=attributes["creation_time"],
        updated_by="unknown",
        updated_at=attributes["modification_time"],
        hidden=False,
    )
