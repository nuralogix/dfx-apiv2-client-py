import base64
from typing import Union

from dfx_apiv2_client import DfxApi


class Measurements(DfxApi):
    @classmethod
    async def create(cls, session, study_id: str, resolution: int = 0, user_profile_id: str = ""):
        data = {
            "StudyID": study_id,
            "Resolution": resolution,
            "UserProfileId": user_profile_id,
        }
        url_fragment = "/".join(__loader__.name.lower().split(".")[1:])
        url = f"{DfxApi.rest_url}/{url_fragment}"
        async with session.post(url, json=data) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body["ID"]

            raise ValueError((url, resp.status, body))

    @classmethod
    async def add_data(cls, session, measurement_id: str, chunk_order: Union[str, int], action: str, start_time: str,
                       end_time: str, metadata: Union[bytes, bytearray, memoryview,
                                                      str], payload: Union[bytes, bytearray, memoryview, str]):
        data = {
            "ChunkOrder": chunk_order,
            "Action": action,
            "StartTime": start_time,
            "EndTime": end_time,
            "Meta": str(metadata),
            "Payload": payload if type(payload) == str else base64.standard_b64encode(payload).decode('ascii')
        }
        url_fragment = "/".join(__loader__.name.lower().split(".")[1:])
        url = f"{DfxApi.rest_url}/{url_fragment}/{measurement_id}/data"
        async with session.post(url, json=data) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body["ID"]

            raise ValueError((url, resp.status, body))