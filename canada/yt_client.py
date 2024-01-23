import json
from contextlib import asynccontextmanager

import aiohttp

from .settings import YT_HOST


class SimpleYtClient:
    def __init__(self, yt_host: str):
        self.yt_host = yt_host
        self._session: aiohttp.ClientSession()

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()

    async def make_request(
            self, method: str, url: str, params: dict = None, headers=None,
            json_data: dict | str | None = None
    ):
        headers = headers or {}
        headers.update({
            "X-YT-Input-Format": "<encode_utf8=%false>json",
            "X-YT-Output-Format": "<encode_utf8=%false>json",
            "X-YT-Header-Format": "<format=text>yson"
        })
        params = params or {}
        resp = await self._session.request(
            method=method, url=f"{self.yt_host}/api/v3/{url}",
            params=params, headers=headers, json=json_data,
        )
        print(resp.status, resp.headers)
        resp.raise_for_status()
        return resp

    @asynccontextmanager
    async def transaction(self):
        tx_id = await self.start_transaction()  # TODO: pass tx_id to all operations?
        try:
            yield
        except Exception:
            raise
        else:
            await self.commit_transaction(tx_id)

    async def start_transaction(self) -> str:
        resp = await self.make_request(
            "POST", "start_tx"
        )
        return (await resp.text())[1:-1]

    async def commit_transaction(self, transaction_id: str):
        await self.make_request(
            "POST", "commit_tx", params={"transaction_id": transaction_id}
        )

    async def create_file(self, file_path: str, ignore_existing: bool = True):
        await self.make_request(
            "POST", "create",
            params={"path": file_path, "type": "file", "ignore_existing": int(ignore_existing)}
        )

    async def write_file(self, file_path: str, file_data: dict):
        await self.make_request("PUT", "write_file", params={"path": file_path}, json_data=file_data)

    async def read_file(self, file_path: str):
        resp = await self.make_request("GET", "read_file", params={"path": file_path})
        return await resp.text()

    async def get_node(self, node_path: str):
        resp = await self.make_request("GET", "get", params={"path": f"{node_path}/@"})
        return await resp.json()

    async def list_dir(self, dir_path: str, attributes: list[str]):
        # resp = await self.make_request(
        #     "GET", "list", params={"path": f"{dir_path}"}
        # )
        resp = await self.make_request(
            "POST", "list", json_data={"path": f"{dir_path}", "attributes": attributes},
        )
        data = await resp.json()
        return data

    async def create_dir(self, dir_path):
        await self.make_request(
            "POST", "create",
            params={"path": dir_path, "type": "map_node", "ignore_existing": 0}
        )

    async def set_attribute(self, node_path: str, attr_name: str, attr_value: str):
        await self.make_request(
            "PUT", "set",
            params={"path": f"{node_path}/@{attr_name}", "encode_utf8": 0}, json_data=attr_value,
        )

    async def delete_node(self, node_path: str):
        await self.make_request(
            "POST", "remove",
            json_data={"path": node_path}
        )


def get_yt_cli():
    return SimpleYtClient(yt_host=YT_HOST)
