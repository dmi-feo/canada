from enum import Enum

from aiohttp import web
from starlette.responses import JSONResponse

from canada.yt_client import get_yt_cli
from canada.settings import YT_HOME_PREFIX


router = web.RouteTableDef()


@router.get('/v1/entries/{entry_id}')
@router.get('/private/entries/{entry_id}')
async def get_entry(entry_id: str) -> JSONResponse:
    async with get_yt_cli() as yt:
        info = await yt.read_file(f"{YT_HOME_PREFIX}/{entry_id}")

    return JSONResponse({
        "entryId": entry_id,
        "scope": "connection",
        "type": "postgres",
        "key": "Marketplace/Sample Superstore/Sample ClickHouse",
        "createdBy": "system",
        "createdAt": "2022-01-02T13:05:46.808Z",
        "updatedBy": "uid:systemId",
        "updatedAt": "2023-09-13T19:03:06.393Z",
        "savedId": "8dmexy9g4ebmx",
        "publishedId": "8dmexy9g4ebmx",
        "revId": "8dmexy9g4ebmx",
        "tenantId": "org_bpf2q5l938o7t1ar5roh",
        "unversionedData": {
            "password": {
                "cypher_text": "gAAAAABld5KhjqI4u0u0h_9eBfmc7_sSzaOSN5ESSKwl088BZdAFmV7OAvL72JGQaT_pWIYFJOQMN5C3JL4IlCznaPp90kDlxQ==",
                "key_kind": "local_fernet",
                "key_id": "key_1"
            },
        },
        "data": {
            "host": "lol",
            "name": None,
            "port": 6432,
            "ssl_ca": None,
            "db_name": "asd",
            "username": "dsa",
            "ssl_enable": False,
            "table_name": None,
            "cache_ttl_sec": None,
            "mdb_folder_id": None,
            "raw_sql_level": "off",
            "mdb_cluster_id": None,
            "enforce_collate": "auto",
            "sample_table_name": None,
            "skip_mdb_org_check": False,
            "is_verified_mdb_org": False,
            "data_export_forbidden": False
        },
        "meta": {
            "state": "saved",
        },
        "hidden": False,
        "public": False,
        "workbookId": "hellothere",  # !!!!!!
        "isFavorite": False,
        "permissions": {
            "execute": True,
            "read": True,
            "edit": True,
            "admin": True
        }
    })


# @app.get('/v2/workbooks/{workbook_id}')
# async def get_workbook(workbook_id: str) -> JSONResponse:


class EntrySaveMode(Enum):
    publish = "publish"
    save = "save"


# class CreateEntryRequest(BaseModel):
#     class Meta(BaseModel):
#         state: str
#
#     scope: str
#     workbookId: str
#     name: str
#     meta: Meta
#     data: dict
#     unversionedData: dict
#     type: str
#     # recursion: bool
#     hidden: bool
#     links: dict
#     mode: EntrySaveMode

#
# @router.post("/v1/entries")
# @router.post("/private/entries")
# async def create_entry(request: CreateEntryRequest) -> JSONResponse:
#     async with get_yt_cli() as yt:
#         async with yt.transaction():
#             await yt.create_file(file_path=f"{YT_HOME_PREFIX}/{request.name}")
#             await yt.write_file(file_path=f"{YT_HOME_PREFIX}/{request.name}", file_data=request.data)
#             # TODO: write meta
#     return JSONResponse({'entryId': f"{request.workbookId}/{request.name}"})