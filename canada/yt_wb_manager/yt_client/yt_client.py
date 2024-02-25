import ssl
from contextlib import asynccontextmanager
from typing import Any

import aiohttp
import attr

from canada.yt_wb_manager.yt_client.auth import BaseYTAuthContext
from canada.yt_wb_manager.constants import YTNodeType, YTLockMode


@attr.s(slots=True)
class SimpleYtClient:
    yt_host: str = attr.ib()
    auth_context: BaseYTAuthContext = attr.ib()
    ca_file: str = attr.ib(default=None)
    _session: aiohttp.ClientSession | None = attr.ib(default=None)

    async def __aenter__(self):
        ssl_context = ssl.create_default_context(cafile=self.ca_file)
        self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()

    async def make_request(
            self, method: str, url: str, params: dict | None = None, headers: dict | None = None,
            json_data: dict | str | None = None, cookies: dict | None = None
    ):
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

        resp = await self._session.request(
            method=method, url=f"{self.yt_host}/api/v3/{url}",
            params=params, headers=headers, json=json_data, cookies=cookies,
        )
        print(resp.status, resp.headers)
        resp.raise_for_status()
        return resp

    @asynccontextmanager
    async def transaction(self, outer_tx_id: str | None = None):  # TODO: ensure all operations in tx send tx_id
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
        return await resp.json()

    async def commit_transaction(self, tx_id: str):
        await self.make_request(
            "POST", "commit_tx", params={"transaction_id": tx_id}
        )

    async def abort_transaction(self, tx_id: str):
        await self.make_request(
            "POST", "abort_tx", params={"transaction_id": tx_id}
        )

    async def create_node(
            self, path: str, node_type: YTNodeType, ignore_existing: bool = True,
            attributes: dict[str, Any] | None = None,
            tx_id: str | None = None
    ):
        attributes = attributes or {}
        resp = await self.make_request(
            "POST", "create",
            params={
                "path": path,
                "type": node_type.value,
                "ignore_existing": int(ignore_existing),
                "transaction_id": tx_id,
            },
            json_data={"attributes": attributes}
        )
        node_id = await resp.json()
        return node_id

    async def write_file(self, node_id: str, file_data: dict, tx_id: str | None = None):
        await self.make_request(
            "PUT", "write_file",
            params={"path": f"#{node_id}", "transaction_id": tx_id}, json_data=file_data
        )

    async def read_file(self, node_id: str, tx_id: str | None = None):
        resp = await self.make_request(
            "GET", "read_file",
            params={"path": f"#{node_id}", "transaction_id": tx_id}
        )
        return await resp.text()

    async def write_document(self, node_id: str, data: dict, tx_id: str | None = None):
        await self.make_request(
            "PUT", "set",
            params={"path": f"#{node_id}", "transaction_id": tx_id}, json_data=data
        )

    async def read_document(self, node_id: str, tx_id: str | None = None):
        resp = await self.make_request(
            "GET", "get",
            params={"path": f"#{node_id}", "transaction_id": tx_id}
        )
        return await resp.json()

    async def get_node_attributes(self, node_id: str, tx_id: str | None = None):
        resp = await self.make_request(
            "GET", "get",
            params={"path": f"#{node_id}/@", "transaction_id": tx_id}
        )
        return await resp.json()

    async def list_dir(self, node_id: str, attributes: list[str], tx_id: str | None = None):
        resp = await self.make_request(
            "POST", "list",
            json_data={"path": f"#{node_id}", "attributes": attributes},
            params={"transaction_id": tx_id}
        )
        data = await resp.json()
        return data

    async def set_attribute(self, node_id: str, attr_name: str, attr_value: str, tx_id: str | None = None):
        await self.make_request(
            "PUT", "set",
            params={
                "path": f"#{node_id}/@{attr_name}",
                "encode_utf8": 0,
                "transaction_id": tx_id,
            },
            json_data=attr_value,
        )

    async def delete_node(self, node_id: str, tx_id: str | None = None):
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

    async def delete_lock(self, node_id: str, tx_id: str):
        await self.make_request(
            "POST", "unlock",
            json_data={"path": f"#{node_id}"},
            params={"transaction_id": tx_id},
        )
