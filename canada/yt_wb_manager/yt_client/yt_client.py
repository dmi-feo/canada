from __future__ import annotations
import ssl
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Self, Type, AsyncIterator
from types import TracebackType

import aiohttp
import attr

from canada.yt_wb_manager.yt_client.auth import BaseYTAuthContext
from canada.yt_wb_manager.constants import YTNodeType, YTLockMode

if TYPE_CHECKING:
    from canada.types import JSON, JSONDict


@attr.s
class YtNode:
    name: str = attr.ib()
    attributes: dict[str, str] = attr.ib()


@attr.s(slots=True)
class SimpleYtClient:
    yt_host: str = attr.ib()
    auth_context: BaseYTAuthContext = attr.ib()
    ca_file: str | None = attr.ib(default=None)
    _session: aiohttp.ClientSession | None = attr.ib(default=None)

    async def __aenter__(self) -> Self:
        ssl_context = ssl.create_default_context(cafile=self.ca_file)
        self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
        return self

    async def __aexit__(
            self, exc_type: Type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
    ) -> None:
        assert self._session is not None
        await self._session.close()

    async def make_request(
            self, method: str, url: str,
            params: dict[str, str | None] | None = None,
            headers: dict[str, str] | None = None,
            json_data: JSON | None = None,
            cookies: dict[str, str] | None = None,
    ) -> aiohttp.ClientResponse:
        headers = headers or {}
        headers.update({
            "X-YT-Input-Format": "<encode_utf8=%false>json",
            "X-YT-Output-Format": "<encode_utf8=%false>json",
            "X-YT-Header-Format": "<format=text>yson",
        })

        params = params or {}
        cookies = cookies or {}

        self.auth_context.mutate_auth_data(cookies=cookies, headers=headers)  # TODO FIXME: it's ugly

        if "transaction_id" in params and params["transaction_id"] is None:
            del params["transaction_id"]

        assert self._session is not None
        resp = await self._session.request(
            method=method, url=f"{self.yt_host}/api/v3/{url}",
            params=params, headers=headers, json=json_data, cookies=cookies,
        )
        print(resp.status, resp.headers)
        resp.raise_for_status()
        return resp

    @asynccontextmanager
    async def transaction(self, outer_tx_id: str | None = None) -> AsyncIterator[str]:
        # TODO: ensure all operations in tx send tx_id
        tx_id = await self.start_transaction(outer_tx_id=outer_tx_id)
        try:
            yield tx_id
        except Exception:
            await self.abort_transaction(tx_id)
            raise
        else:
            await self.commit_transaction(tx_id)

    async def start_transaction(self, outer_tx_id: str | None = None) -> str:
        resp = await self.make_request(
            "POST", "start_tx",
            params={"transaction_id": outer_tx_id}
        )
        return str(await resp.json())

    async def commit_transaction(self, tx_id: str) -> None:
        await self.make_request(
            "POST", "commit_tx", params={"transaction_id": tx_id}
        )

    async def abort_transaction(self, tx_id: str) -> None:
        await self.make_request(
            "POST", "abort_tx", params={"transaction_id": tx_id}
        )

    async def create_node(
            self, path: str, node_type: YTNodeType, ignore_existing: bool = True,
            attributes: JSONDict | None = None,
            tx_id: str | None = None
    ) -> str:
        attributes = attributes or {}
        resp = await self.make_request(
            "POST", "create",
            params={
                "path": path,
                "type": node_type.value,
                "ignore_existing": str(int(ignore_existing)),
                "transaction_id": tx_id,
            },
            json_data={"attributes": attributes}
        )
        node_id = str(await resp.json())
        return node_id

    async def write_file(self, node_id: str, file_data: JSON, tx_id: str | None = None) -> None:
        await self.make_request(
            "PUT", "write_file",
            params={"path": f"#{node_id}", "transaction_id": tx_id}, json_data=file_data
        )

    async def read_file(self, node_id: str, tx_id: str | None = None) -> str:
        resp = await self.make_request(
            "GET", "read_file",
            params={"path": f"#{node_id}", "transaction_id": tx_id}
        )
        return await resp.text()

    async def write_document(self, node_id: str, data: JSON, tx_id: str | None = None) -> None:
        await self.make_request(
            "PUT", "set",
            params={"path": f"#{node_id}", "transaction_id": tx_id}, json_data=data
        )

    async def read_document(self, node_id: str, tx_id: str | None = None) -> JSON:
        resp = await self.make_request(
            "GET", "get",
            params={"path": f"#{node_id}", "transaction_id": tx_id}
        )
        data = await resp.json()
        assert isinstance(data, dict)
        return data

    async def get_node_attributes(self, node_id: str, tx_id: str | None = None) -> dict[str, str]:
        resp = await self.make_request(
            "GET", "get",
            params={"path": f"#{node_id}/@", "transaction_id": tx_id}
        )
        data = await resp.json()
        assert isinstance(data, dict)
        return data

    async def list_dir(
            self, node_id: str, attributes: list[str], tx_id: str | None = None
    ) -> list[YtNode]:
        resp = await self.make_request(
            "POST", "list",
            # error: Dict entry 1 has incompatible type "str": "list[str]";
            # expected "str": "dict[str, JSON] | list[JSON] | str | int | float | None"  [dict-item]
            json_data={"path": f"#{node_id}", "attributes": attributes},  # type: ignore
            params={"transaction_id": tx_id}
        )
        data = await resp.json()
        assert isinstance(data, list)
        nodes = [YtNode(name=item["$value"], attributes=item["$attributes"]) for item in data]
        return nodes

    async def set_attribute(self, node_id: str, attr_name: str, attr_value: str, tx_id: str | None = None) -> None:
        await self.make_request(
            "PUT", "set",
            params={
                "path": f"#{node_id}/@{attr_name}",
                "encode_utf8": "0",
                "transaction_id": tx_id,
            },
            json_data=attr_value,
        )

    async def delete_node(self, node_id: str, tx_id: str | None = None) -> None:
        await self.make_request(
            "POST", "remove",
            json_data={"path": f"#{node_id}"},
            params={"transaction_id": tx_id}
        )

    async def set_lock(
            self, node_id: str, tx_id: str, mode: YTLockMode, waitable: bool = False
    ) -> str:
        await self.make_request(
            "POST", "lock",
            json_data={"path": f"#{node_id}", "mode": mode.value, "waitable": waitable},
            params={"transaction_id": tx_id},
        )
        return tx_id

    async def delete_lock(self, node_id: str, tx_id: str) -> None:
        await self.make_request(
            "POST", "unlock",
            json_data={"path": f"#{node_id}"},
            params={"transaction_id": tx_id},
        )
