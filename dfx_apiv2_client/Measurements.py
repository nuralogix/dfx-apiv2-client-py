# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

import base64
import json
from typing import Any, Union

import aiohttp

from .Base import Base


class Measurements(Base):
    url_fragment = "measurements"

    @classmethod
    async def create(cls,
                     session: aiohttp.ClientSession,
                     study_id: str,
                     resolution: int = 0,
                     user_profile_id: str = "",
                     partner_id: str = "",
                     streaming: bool = False,
                     **kwargs: Any) -> Any:
        data = {
            "StudyID": study_id,
            "Resolution": resolution,
            "UserProfileID": user_profile_id,
            "PartnerID": partner_id,
        }
        if streaming:
            data["Mode"] = "STREAMING"

        return await cls._post(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def add_data(cls,
                       session: aiohttp.ClientSession,
                       measurement_id: str,
                       chunk_order: Union[str, int],
                       action: str,
                       start_time_s: str,
                       end_time_s: str,
                       duration_s: str,
                       metadata: Union[bytes, bytearray, memoryview],
                       payload: Union[bytes, bytearray, memoryview],
                       **kwargs: Any) -> Any:
        data = {
            "ChunkOrder": chunk_order,
            "Action": action,
            "StartTime": start_time_s,
            "EndTime": end_time_s,
            "Duration": duration_s,
            "Meta": base64.standard_b64encode(metadata).decode('ascii'),
            "Payload": base64.standard_b64encode(payload).decode('ascii'),
        }

        return await cls._post(session, f"{cls.url_fragment}/{measurement_id}/data", data=data, **kwargs)

    @classmethod
    async def list(cls,
                   session: aiohttp.ClientSession,
                   date: str = "",
                   end_date: str = "",
                   user_profile_id: str = "",
                   user_profile_name: str = "",
                   study_id: str = "",
                   status_id: str = "",
                   partner_id: str = "",
                   limit: int = 50,
                   offset: int = 0,
                   **kwargs: Any) -> Any:
        params = {
            "Date": date,
            "EndDate": end_date,
            "UserProfileID": user_profile_id,
            "UserProfileName": user_profile_name,
            "StudyID": study_id,
            "StatusID": status_id,
            "PartnerID": partner_id,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, cls.url_fragment, params=params, **kwargs)

    @classmethod
    async def retrieve(cls,
                       session: aiohttp.ClientSession,
                       measurement_id: str,
                       expand: bool = True,
                       **kwargs: Any) -> Any:
        params = {}
        if expand:
            params["ExpandResults"] = "true"
        return await cls._get(session, f"{cls.url_fragment}/{measurement_id}", params=params, **kwargs)

    @classmethod
    async def ws_subscribe_to_results(cls, ws: aiohttp.ClientWebSocketResponse, request_id: Union[str, int],
                                      measurement_id: str, results_request_id: Union[str, int]) -> None:
        action_id = "0510"

        request = {
            "Params": {
                "ID": measurement_id,
            },
            "RequestID": str(results_request_id),
        }

        ws_request = f"{action_id:4}{request_id:10}{json.dumps(request)}"

        await ws.send_str(ws_request)

    @classmethod
    async def ws_add_data(
        cls,
        ws: aiohttp.ClientWebSocketResponse,
        request_id: str,
        measurement_id: str,
        chunk_order: Union[str, int],
        action: str,
        start_time_s: str,
        end_time_s: str,
        duration_s: str,
        metadata: Union[bytes, bytearray, memoryview],
        payload: Union[bytes, bytearray, memoryview],
    ) -> None:
        action_id = "0506"

        request = {
            "Params": {
                "ID": measurement_id,
            },
            "ChunkOrder": int(chunk_order),
            "Action": action,
            "StartTime": start_time_s,
            "EndTime": end_time_s,
            "Duration": int(duration_s),
            "Meta": base64.standard_b64encode(metadata).decode('ascii'),
            "Payload": base64.standard_b64encode(payload).decode('ascii'),
        }

        ws_request = f"{action_id:4}{request_id:10}{json.dumps(request)}"

        await ws.send_str(ws_request)

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, measurement_id: str, **kwargs: Any) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/{measurement_id}", **kwargs)
