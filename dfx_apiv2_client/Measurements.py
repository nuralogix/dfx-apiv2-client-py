# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

import base64
import json
import warnings
from typing import Any, Union, Optional

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
                     **kwargs: Any) -> Any:
        """
        Create a new measurement.

        :param session: The aiohttp ClientSession to use.
        :param study_id: The ID of the study to associate with the measurement.
        :param resolution: The resolution of the measurement (0 or 100).
        :param user_profile_id: The ID of the user profile to associate with the measurement.
        :param partner_id: The ID of the partner to associate with the measurement.
        :return: The response from the API.
        """
        data = {
            "StudyID": study_id,
            "Resolution": resolution,
            "UserProfileID": user_profile_id,
            "PartnerID": partner_id,
        }

        return await cls._post(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def add_data(cls,
                       session: aiohttp.ClientSession,
                       measurement_id: str,
                       action: str,
                       payload: Union[bytes, bytearray, memoryview],
                       *,
                       chunk_order: Optional[Union[str, int]] = None,
                       start_time_s: Optional[str] = None,
                       end_time_s: Optional[str] = None,
                       duration_s: Optional[str] = None,
                       metadata: Optional[Union[bytes, bytearray, memoryview]] = None,
                       **kwargs: Any) -> Any:
        """
        Add data to a measurement.

        :param session: The aiohttp ClientSession to use.
        :param measurement_id: The ID of the measurement.
        :param action: The action to perform (e.g. CHUNK::PROCESS).
        :param payload: The data payload to add.
        :param chunk_order: The order of the chunk.
        :param start_time_s: The start time of the chunk in seconds.
        :param end_time_s: The end time of the chunk in seconds.
        :param duration_s: The duration of the chunk in seconds.
        :param metadata: Additional metadata for the chunk.
        :return: The response from the API.
        """
        data = {
            "Action": action,
            "Payload": base64.standard_b64encode(payload).decode('ascii'),
        }
        data = {k: v for k, v in data.items() if v is not None}

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
                   mode: str = "",
                   limit: int = 50,
                   offset: int = 0,
                   **kwargs: Any) -> Any:
        """
        List measurements.

        :param session: The aiohttp ClientSession to use.
        :param date: Filter by date (YYYY-MM-DD).
        :param end_date: Filter by end date (YYYY-MM-DD).
        :param user_profile_id: Filter by user profile ID.
        :param user_profile_name: Filter by user profile name.
        :param study_id: Filter by study ID.
        :param status_id: Filter by status ID.
        :param partner_id: Filter by partner ID.
        :param mode: Filter by mode.
        :param limit: The number of results to return.
        :param offset: The offset to start returning results from.
        :return: The response from the API.
        """
        params = {
            "Date": date,
            "EndDate": end_date,
            "UserProfileID": user_profile_id,
            "UserProfileName": user_profile_name,
            "StudyID": study_id,
            "StatusID": status_id.upper(),
            "PartnerID": partner_id,
            "Mode": mode.upper(),
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
        """
        Retrieve a measurement by its ID.

        :param session: The aiohttp ClientSession to use.
        :param measurement_id: The ID of the measurement to retrieve.
        :param expand: Whether to expand the results.
        :return: The response from the API.
        """
        params = {}
        if expand:
            params["ExpandResults"] = "true"
        return await cls._get(session, f"{cls.url_fragment}/{measurement_id}", params=params, **kwargs)

    @classmethod
    async def ws_subscribe_to_results(cls, ws: aiohttp.ClientWebSocketResponse, request_id: Union[str, int],
                                      measurement_id: str, results_request_id: Union[str, int]) -> None:
        """
        Subscribe to measurement results via WebSocket.

        :param ws: The WebSocket connection.
        :param request_id: The request ID.
        :param measurement_id: The ID of the measurement.
        :param results_request_id: The request ID for the results.
        """
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
        action: str,
        payload: Union[bytes, bytearray, memoryview],
        *,
        chunk_order: Optional[Union[str, int]] = None,
        start_time_s: Optional[str] = None,
        end_time_s: Optional[str] = None,
        duration_s: Optional[str] = None,
        metadata: Optional[Union[bytes, bytearray, memoryview]] = None,
    ) -> None:
        """
        Add data to a measurement via WebSocket.

        :param ws: The WebSocket connection.
        :param request_id: The request ID.
        :param measurement_id: The ID of the measurement.
        :param action: The action to perform (e.g. CHUNK::PROCESS).
        :param payload: The data payload to add.
        :param chunk_order: The order of the chunk.
        :param start_time_s: The start time of the chunk in seconds.
        :param end_time_s: The end time of the chunk in seconds.
        :param duration_s: The duration of the chunk in seconds.
        :param metadata: Additional metadata for the chunk.
        """
        action_id = "0506"

        request = {
            "Params": {
                "ID": measurement_id,
            },
            "Action": action,
            "Payload": base64.standard_b64encode(payload).decode('ascii'),
        }
        request = {k: v for k, v in request.items() if v is not None}

        ws_request = f"{action_id:4}{request_id:10}{json.dumps(request)}"

        await ws.send_str(ws_request)

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, measurement_id: str, **kwargs: Any) -> Any:
        """
        Delete a measurement.

        :param session: The aiohttp ClientSession to use.
        :param measurement_id: The ID of the measurement to delete.
        :return: The response from the API.
        """
        warnings.warn(f"{cls.delete.__qualname__} is deprecated and will be removed.", DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{measurement_id}", **kwargs)

    @classmethod
    async def retrieve_intermediate(cls,
                       session: aiohttp.ClientSession,
                       measurement_id: str,
                       chunk_order: int,
                       **kwargs: Any) -> Any:
        """
        Retrieve intermediate results for a measurement.

        :param session: The aiohttp ClientSession to use.
        :param measurement_id: The ID of the measurement.
        :param chunk_order: The order of the chunk to retrieve results for.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/{measurement_id}/results/{chunk_order}", **kwargs)
