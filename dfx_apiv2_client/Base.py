# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

import json
from typing import Any, Tuple, Union

import aiohttp

from .Settings import Settings


class Base:
    @classmethod
    async def _get(cls, session: aiohttp.ClientSession, url_fragment: str, params: dict = None, **kwargs: Any) -> Any:
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.get(url, params=params, **kwargs) as resp:
            if resp.content_type != "application/json":
                return resp.status, await resp.read()
            else:
                return resp.status, await resp.json()

    @classmethod
    async def _post(cls, session: aiohttp.ClientSession, url_fragment: str, data: Union[dict, list],
                    **kwargs: Any) -> Any:
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.post(url, json=data, **kwargs) as resp:
            return resp.status, await resp.json()

    @classmethod
    async def _patch(cls, session: aiohttp.ClientSession, url_fragment: str, data: dict, **kwargs: Any) -> Any:
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.patch(url, json=data, **kwargs) as resp:
            return resp.status, await resp.json()

    @classmethod
    async def _delete(cls,
                      session: aiohttp.ClientSession,
                      url_fragment: str,
                      data: Union[dict, list] = None,
                      **kwargs: Any) -> Any:
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.delete(url, json=data, **kwargs) as resp:
            return resp.status, await resp.json()

    @classmethod
    def ws_decode(cls, msg: aiohttp.WSMessage) -> Tuple[int, str, bytes]:
        if msg.type != aiohttp.WSMsgType.BINARY:
            raise ValueError("WebSocket error: Expecting only binary websocket responses")
        result = msg.data
        request_id = result[:10].decode('utf-8')
        status = int(result[10:13].decode('utf-8'))
        payload = result[13:].decode('utf-8')

        # TODO: Handle raise_for_status == False
        if status >= 400:
            try:
                error = json.loads(payload)
            except Exception as e:
                raise ValueError(
                    f"WebSocket error: API Status {status} for req#:{request_id}, could not parse response as JSON"
                ) from e
            raise ValueError(f"WebSocket error: API Status {status} for req#:{request_id}, Code: {error['Code']}, "
                             f"Description: '{error['Errors'] if 'Errors' in error else None}'.")

        return status, request_id, payload

    @classmethod
    def ws_connect(cls, session: aiohttp.ClientSession, **kwargs: Any):
        return session.ws_connect(Settings.ws_url, protocols=["json"], **kwargs)
