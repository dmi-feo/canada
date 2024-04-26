from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import web

from canada.aiohttp_marshmallow.base import with_schema
import canada.api.collection.schema as sch
from canada.app_stuff import BaseView


if TYPE_CHECKING:
    from canada.types import (
        JSON,
        JSONDict,
    )


router = web.RouteTableDef()


@router.view("/v1/root-collection-permissions")
class RootCollectionPermissionsView(BaseView):
    @with_schema(resp_schema=sch.RootCollectionPermissionsResponse)
    async def get(self, data: JSONDict) -> JSON:
        """
        Get root collection permissions
        """
        return {
            "createCollectionInRoot": True,
            "createWorkbookInRoot": True,
        }


@router.view("/v1/collection-content")
class CollectionContentView(BaseView):
    @with_schema(resp_schema=sch.CollectionContentResponseSchema)
    async def get(self, data: JSONDict) -> JSON:
        """
        Get collection content
        """
        collection_id = self.request.query.get("collectionId")

        coll_content = await self.app_services.wbman.list_collection(collection_id)

        return {
            "collections": [
                self.app_services.api_serializer.serialize_collection(coll) for coll in coll_content.collections
            ],
            "collectionsNextPageToken": None,
            "workbooks": [self.app_services.api_serializer.serialize_workbook(wb) for wb in coll_content.workbooks],
            "workbooksNextPageToken": None,
        }


@router.view("/v1/collections/{collection_id}")
class CollectionItemView(BaseView):
    @with_schema(resp_schema=sch.CollectionResponseSchema)
    async def get(self, data: JSONDict) -> JSON:
        """
        Get collection info
        """
        collection_id = self.request.match_info["collection_id"]
        collection = await self.app_services.wbman.get_collection(collection_id)
        return self.app_services.api_serializer.serialize_collection(collection)

    @with_schema(resp_schema=sch.DeleteCollectionResponse)
    async def delete(self, data: JSONDict) -> JSON:
        """
        Delete collection
        """
        collection_id = self.request.match_info["collection_id"]
        await self.app_services.wbman.delete_collection(collection_id)
        return {}


@router.view("/v1/collections")
class CollectionsView(BaseView):
    @with_schema(req_schema=sch.CreateCollectionRequest, resp_schema=sch.CreateCollectionResponse)
    async def post(self, data: JSONDict) -> JSON:
        """
        Create collection
        """
        collection = self.app_services.api_serializer.deserialize_collection(data)
        collection_id = await self.app_services.wbman.create_collection(collection)
        saved_collection = await self.app_services.wbman.get_collection(collection_id)
        return self.app_services.api_serializer.serialize_collection(saved_collection)


@router.view("/v1/collections/{collection_id}/breadcrumbs")
class CollectionBreadcrumbsView(BaseView):
    @with_schema(resp_schema=sch.CollectionBreadcrumbsResponse)
    async def get(self, data: JSONDict) -> JSON:
        """
        Get collection breadcrumbs
        """
        resp_data = []
        collection_id: str | None = self.request.match_info["collection_id"]

        while collection_id is not None:
            collection = await self.app_services.wbman.get_collection(collection_id)
            resp_data.append(
                {
                    "collectionId": collection.collection_id,
                    "title": collection.title,
                }
            )
            collection_id = collection.parent_id

        # Incompatible return value type (got "list[dict[str, str | None]]",
        # expected "dict[str, JSON] | list[JSON] | str | int | float | bool | None")  [return-value]
        return resp_data[::-1]  # type: ignore
