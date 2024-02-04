from enum import Enum

from aiohttp import web

from canada.app_stuff import AppServices
from canada.id import ID
from canada.aiohttp_marshmallow.base import response_schema, request_schema
from canada.api.entry import schema


router = web.RouteTableDef()


@router.get('/v1/entries/{entry_id}')
@router.get('/private/entries/{entry_id}')
@response_schema(schema.GetEntryResponse)
async def get_entry(request, app_services: AppServices):
    entry_id = ID.from_str(request.match_info["entry_id"])
    entry = await app_services.wbman.get_entry(entry_id)

    return entry

    # return JSONResponse({
    #     "entryId": entry_id,
    #     "scope": "connection",
    #     "type": "postgres",
    #     "key": "Marketplace/Sample Superstore/Sample ClickHouse",
    #     "createdBy": "system",
    #     "createdAt": "2022-01-02T13:05:46.808Z",
    #     "updatedBy": "uid:systemId",
    #     "updatedAt": "2023-09-13T19:03:06.393Z",
    #     "savedId": "8dmexy9g4ebmx",
    #     "publishedId": "8dmexy9g4ebmx",
    #     "revId": "8dmexy9g4ebmx",
    #     "tenantId": "org_bpf2q5l938o7t1ar5roh",
    #     "unversionedData": {
    #         "password": {
    #             "cypher_text": "gAAAAABld5KhjqI4u0u0h_9eBfmc7_sSzaOSN5ESSKwl088BZdAFmV7OAvL72JGQaT_pWIYFJOQMN5C3JL4IlCznaPp90kDlxQ==",
    #             "key_kind": "local_fernet",
    #             "key_id": "key_1"
    #         },
    #     },
    #     "data": {
    #         "host": "lol",
    #         "name": None,
    #         "port": 6432,
    #         "ssl_ca": None,
    #         "db_name": "asd",
    #         "username": "dsa",
    #         "ssl_enable": False,
    #         "table_name": None,
    #         "cache_ttl_sec": None,
    #         "mdb_folder_id": None,
    #         "raw_sql_level": "off",
    #         "mdb_cluster_id": None,
    #         "enforce_collate": "auto",
    #         "sample_table_name": None,
    #         "skip_mdb_org_check": False,
    #         "is_verified_mdb_org": False,
    #         "data_export_forbidden": False
    #     },
    #     "meta": {
    #         "state": "saved",
    #     },
    #     "hidden": False,
    #     "public": False,
    #     "workbookId": "hellothere",  # !!!!!!
    #     "isFavorite": False,
    #     "permissions": {
    #         "execute": True,
    #         "read": True,
    #         "edit": True,
    #         "admin": True
    #     }
    # })


class EntrySaveMode(Enum):
    publish = "publish"
    save = "save"


@router.post("/v1/entries")
@router.post("/private/entries")
@request_schema(schema.CreateEntryRequest)
@response_schema(schema.CreateEntryResponse)
async def create_entry(request, verified_json: dict, app_services: AppServices):
    entry_id = await app_services.wbman.create_entry(
        name=verified_json["name"],
        workbook_id=ID.from_str(verified_json["workbook_id"]),
        entry_data=verified_json["data"],
        unversioned_data=verified_json["unversioned_data"],
        scope=verified_json["scope"],
        entry_type=verified_json["type"],
    )

    return {"entry_id": entry_id}


@router.post("/v1/entries/{entry_id}")
@request_schema(schema.UpdateEntryRequest)
@response_schema(schema.UpdateEntryResponse)
async def update_entry(request, verified_json: dict, app_services: AppServices):
    entry_id = ID.from_str(request.match_info["entry_id"])
    await app_services.wbman.update_entry(
        entry_id=entry_id,
        entry_data=verified_json["data"],
        unversioned_data=verified_json["unversioned_data"],
    )

    return {"entry_id": entry_id}
