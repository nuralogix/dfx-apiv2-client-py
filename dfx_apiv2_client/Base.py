from typing import Any, Tuple, Union

import aiohttp

from dfx_apiv2_protos import util_pb2

from .Settings import Settings


class Base:
    @classmethod
    async def _get(cls, session: aiohttp.ClientSession, url_fragment: str, params: dict = None) -> Any:
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.get(url, params=params) as resp:
            return await resp.json()

    @classmethod
    async def _post(cls, session: aiohttp.ClientSession, url_fragment: str, data: Union[dict, list]) -> Any:
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.post(url, json=data) as resp:
            return await resp.json()

    @classmethod
    async def _patch(cls, session: aiohttp.ClientSession, url_fragment: str, data: dict) -> Any:
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.patch(url, json=data) as resp:
            return await resp.json()

    @classmethod
    async def _delete(cls, session: aiohttp.ClientSession, url_fragment: str, data: Union[dict, list] = None) -> Any:
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.delete(url, json=data) as resp:
            return await resp.json()

    @classmethod
    def ws_decode(cls, msg: aiohttp.WSMessage) -> Tuple[int, str, bytes]:
        if msg.type != aiohttp.WSMsgType.BINARY:
            raise ValueError("Expecting only binary websocket responses")
        result = msg.data
        request_id = result[:10].decode('utf-8')
        status = int(result[10:13].decode('utf-8'))
        payload = result[13:]

        if status >= 400:
            error = util_pb2.Error()
            try:
                error.ParseFromString(payload)
            except Exception:
                pass
            raise ValueError(
                f"Status {status} for req#:{request_id}, Code: {error.Code}, Message: '{error.Message}', Description: '{error.Errors}'."
            )

        return status, request_id, payload
