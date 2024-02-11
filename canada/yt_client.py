from contextlib import asynccontextmanager

import aiohttp


class TxAlreadyStarted(Exception):
    pass


class SimpleYtClient:
    def __init__(self, yt_host: str):
        self.yt_host = yt_host
        # client must be created per requests, so it's not going to be an issue
        self._session: aiohttp.ClientSession()
        self._curr_tx_id: str | None = None

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

        if self._curr_tx_id is not None:
            params["transaction_id"] = self._curr_tx_id

        resp = await self._session.request(
            method=method, url=f"{self.yt_host}/api/v3/{url}",
            params=params, headers=headers, json=json_data,
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
