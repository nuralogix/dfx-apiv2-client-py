import base64
from typing import Any, Union

import aiohttp

from dfx_apiv2_protos import measurements_pb2

from .Base import Base


class Measurements(Base):
    url_fragment = "measurements"

    @classmethod
    async def create(cls,
                     session: aiohttp.ClientSession,
                     study_id: str,
                     resolution: int = 0,
                     user_profile_id: str = "",
                     **kwargs: Any) -> Any:
        data = {
            "StudyID": study_id,
            "Resolution": resolution,
            "UserProfileId": user_profile_id,
        }

        body = await cls._post(session, cls.url_fragment, data=data, **kwargs)

        return body["ID"]

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

        body = await cls._post(session, f"{cls.url_fragment}/{measurement_id}/data", data=data, **kwargs)

        return body["ID"]

    @classmethod
    async def list(cls,
                   session: aiohttp.ClientSession,
                   date: str = "",
                   end_date: str = "",
                   user_profile_id: str = "",
                   user_profile_name: str = "",
                   study_id: str = "",
                   status_id: str = "",
                   limit: int = 50,
                   offset: int = 0,
                   **kwargs: Any) -> Any:
        """Get a list of historical measurements

        Arguments:
            session {aiohttp.ClientSession} -- The client session

        Keyword Arguments:
            date {str} -- The date to return measurements for yyyy-mm-dd (default: {None})
            end_date {str} -- End date for range of measurements to receive (default: {None})
            user_profile_id {str} -- filter by a Profile ID (default: {None})
            user_profile_name {str} -- filter by a Profile Name (default: {None})
            study_id {str} -- filter by Study ID (default: {None})
            status_id {str} -- filter by measurement Status (default: {None})
            limit {int} -- Number of measurement records to return (default: {50})
            offset {int} -- Offset to specify the start of the count (default: {0})

        Returns:
            [type] -- [description]
        """
        params = {
            "Date": date,
            "EndDate": end_date,
            "UserProfileID": user_profile_id,
            "UserProfileName": user_profile_name,
            "StudyID": study_id,
            "StatusID": status_id,
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
        params = {
            "ExpandResults": "true" if expand else "",
        }
        return await cls._get(session, f"{cls.url_fragment}/{measurement_id}", params=params, **kwargs)

    @classmethod
    async def ws_subscribe_to_results(cls, ws: aiohttp.ClientWebSocketResponse, request_id: str,
                                      measurement_id: str) -> None:
        action_id = "0510"

        proto = measurements_pb2.SubscribeResultsRequest()
        proto.RequestID = str(request_id)
        proto.Params.ID = measurement_id

        ws_request = f"{action_id:4}{request_id:10}".encode() + proto.SerializeToString()

        await ws.send_bytes(ws_request)

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

        proto = measurements_pb2.DataRequest()
        proto.Params.ID = measurement_id
        proto.ChunkOrder = int(chunk_order)
        proto.Action = action
        proto.StartTime = start_time_s
        proto.EndTime = end_time_s
        proto.Duration = int(duration_s)
        proto.Meta = metadata
        proto.Payload = payload

        ws_request = f"{action_id:4}{request_id:10}".encode() + proto.SerializeToString()

        await ws.send_bytes(ws_request)
