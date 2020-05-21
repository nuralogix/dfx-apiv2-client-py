from dfx_apiv2_client import DfxApi


class Organizations(DfxApi):
    url_fragment = "organizations"

    class Licenses(DfxApi):
        url_fragment = "organizations/licenses"

        @classmethod
        async def register(cls, session, license_key: str, device_type_id: str, app_name: str, app_id: str,
                           app_version: str):
            data = {
                "Key": license_key,
                "DeviceTypeID": device_type_id,
                "Name": app_name,
                "Identifier": app_id,
                "Version": app_version
            }
            url = f"{DfxApi.rest_url}/{cls.url_fragment}"
            async with session.post(url, json=data) as resp:
                body = await resp.json()
                if resp.status == 200:
                    DfxApi.device_id = body["DeviceID"]
                    DfxApi.device_token = body["Token"]
                    DfxApi.role_id = body["RoleID"]
                    DfxApi.user_id = body["UserID"]
                    return body

                raise ValueError((url, resp.status, body))

    # [ 809, "1.0", "POST", "getConfig", "/studies/sdkconfig" ],
    # [ 810, "1.0", "POST", "getConfigHash", "/studies/sdkconfig/hash" ]
