from .Settings import Settings


class Organizations:
    url_fragment = "organizations"

    class Licenses:
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
            url = f"{Settings.rest_url}/{cls.url_fragment}"
            async with session.post(url, json=data) as resp:
                body = await resp.json()
                if resp.status == 200:
                    Settings.device_id = body["DeviceID"]
                    Settings.device_token = body["Token"]
                    Settings.role_id = body["RoleID"]
                    Settings.user_id = body["UserID"]
                    return body

                raise ValueError((url, resp.status, body))

    # [ 809, "1.0", "POST", "getConfig", "/studies/sdkconfig" ],
    # [ 810, "1.0", "POST", "getConfigHash", "/studies/sdkconfig/hash" ]
