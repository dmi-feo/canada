import ssl
from contextlib import asynccontextmanager

import aiohttp
import attr

from canada.wb_manager.yt_client.auth import BaseYTAuthContext
from canada.wb_manager.yt_client.exc import TxAlreadyStarted


@attr.s(slots=True)
class SimpleYtClient:
    yt_host: str = attr.ib()
    auth_context: BaseYTAuthContext = attr.ib()
    ca_file: str = attr.ib(default=None)
    _curr_tx_id: str | None = attr.ib(default=None)
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
        if self._curr_tx_id is not None:
            params["transaction_id"] = self._curr_tx_id

        cookies = cookies or {}

        self.auth_context.mutate_auth_data(cookies=cookies, headers=headers)  # TODO FIXME: it's ugly

        resp = await self._session.request(
            method=method, url=f"{self.yt_host}/api/v3/{url}",
            params=params, headers=headers, json=json_data, cookies=cookies,
        )
        print(resp.status, resp.headers)
        resp.raise_for_status()
        return resp

    @asynccontextmanager
    async def transaction(self):
        if self._curr_tx_id is not None:
            raise TxAlreadyStarted()
        self._curr_tx_id = await self.start_transaction()
        try:
            yield
        except Exception:
            await self.abort_transaction(self._curr_tx_id)
            raise
        else:
            await self.commit_transaction(self._curr_tx_id)
        finally:
            self._curr_tx_id = None

    async def start_transaction(self) -> str:
        resp = await self.make_request(
            "POST", "start_tx"
        )
        return await resp.json()

    async def commit_transaction(self, transaction_id: str):
        await self.make_request(
            "POST", "commit_tx", params={"transaction_id": transaction_id}
        )

    async def abort_transaction(self, transaction_id: str):
        await self.make_request(
            "POST", "abort_tx", params={"transaction_id": transaction_id}
        )

    async def create_file(self, file_path: str, ignore_existing: bool = True) -> str:
        resp = await self.make_request(
            "POST", "create",
            params={"path": file_path, "type": "file", "ignore_existing": int(ignore_existing)}
        )
        data = await resp.json()
        return data  # string with id

    async def write_file(self, node_id: str, file_data: dict):
        await self.make_request("PUT", "write_file", params={"path": f"#{node_id}"}, json_data=file_data)

    async def read_file(self, node_id: str):
        resp = await self.make_request("GET", "read_file", params={"path": f"#{node_id}"})
        return await resp.text()

    async def create_document(self, node_path: str, data: dict, ignore_existing: bool = True) -> str:
        resp = await self.make_request(
            "POST", "create",
            params={"path": node_path, "type": "document", "ignore_existing": int(ignore_existing)},
            json_data={"attributes": {"value": data}}
        )
        data = await resp.json()
        return data  # string with id

    async def write_document(self, node_id: str, data: dict):
        await self.make_request("PUT", "set", params={"path": f"#{node_id}"}, json_data=data)

    async def read_document(self, node_id: str):
        resp = await self.make_request("GET", "get", params={"path": f"#{node_id}"})
        return await resp.json()

    async def get_node_attributes(self, node_id: str):
        resp = await self.make_request("GET", "get", params={"path": f"#{node_id}/@"})
        return await resp.json()

    async def list_dir(self, node_id: str, attributes: list[str]):
        resp = await self.make_request(
            "POST", "list", json_data={"path": f"#{node_id}", "attributes": attributes},
        )
        data = await resp.json()
        return data

    async def create_dir(self, dir_path: str) -> str:
        resp = await self.make_request(
            "POST", "create",
            params={"path": dir_path, "type": "map_node", "ignore_existing": 0}
        )
        data = await resp.json()
        return data  # string with id

    async def set_attribute(self, node_id: str, attr_name: str, attr_value: str):
        await self.make_request(
            "PUT", "set",
            params={"path": f"#{node_id}/@{attr_name}", "encode_utf8": 0}, json_data=attr_value,
        )

    async def delete_node(self, node_id: str):
        await self.make_request(
            "POST", "remove",
            json_data={"path": f"#{node_id}"}
        )
