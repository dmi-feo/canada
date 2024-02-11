from __future__ import annotations
import typing

from aiohttp import web

import canada.api.collection.schema as sch
from canada.aiohttp_marshmallow.base import response_schema, request_schema
from canada.wb_manager.exc import RootCollectionCannotBeRequested

if typing.TYPE_CHECKING:
    from canada.app_stuff import AppServices


router = web.RouteTableDef()


@router.get('/v1/root-collection-permissions')
@response_schema(sch.RootCollectionPermissionsResponse)
async def get_root_collection_permissions(request, app_services: AppServices):
    return {
        "create_collection_in_root": True,
        "create_workbook_in_root": True,
    }


@router.get("/v1/collection-content")
@response_schema(sch.CollectionContentResponseSchema)
async def collection_content(request, app_services: AppServices):
    collection_id = request.query.get("collectionId")

    coll_content = await app_services.wbman.list_collection(collection_id)

    return {
        "collections": coll_content.collections,
        "collections_next_page_token": None,
        "workbooks": coll_content.workbooks,
        "workbooks_next_page_token": None,
    }


@router.get("/v1/collections/{collection_id}")
@response_schema(sch.CollectionResponseSchema)
async def get_collection(request, app_services: AppServices):
    collection_id = request.match_info["collection_id"]
    data = await app_services.wbman.get_collection(collection_id)
    return data


@router.delete("/v1/collections/{collection_id}")
@response_schema(sch.DeleteCollectionResponse)
async def delete_collection(request, app_services: AppServices):
    collection_id = request.match_info["collection_id"]
    await app_services.wbman.delete_collection(collection_id)
    return {}


@router.post("/v1/collections")
@request_schema(sch.CreateCollectionRequest)
@response_schema(sch.CreateCollectionResponse)
async def create_collection(request, verified_json: dict, app_services: AppServices):
    collection_id = await app_services.wbman.create_collection(
        title=verified_json["title"],
        parent_id=verified_json["parent_id"],
        description=verified_json["description"],
    )
    data = await app_services.wbman.get_collection(collection_id)
    return data


@router.get("/v1/collections/{collection_id}/breadcrumbs")
@response_schema(sch.CollectionBreadcrumbsResponse)
async def get_collection_breadcrumbs(request, app_services: AppServices):
    collection_id = request.match_info["collection_id"]
    collection = await app_services.wbman.get_collection(collection_id)

    resp_data = [{
        "collection_id": collection.collection_id,
        "title": collection.title,
    }]
    while collection.parent_id:
        try:
            collection = await app_services.wbman.get_collection(collection.parent_id)
        except RootCollectionCannotBeRequested:
            break
        resp_data.append({
            "collection_id": collection.collection_id,
            "title": collection.title,
        })

    return reversed(resp_data)
