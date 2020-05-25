from .Base import Base
from .Settings import Settings


class Organizations(Base):
    url_fragment = "organizations"

    @classmethod
    async def register_license(cls, session, license_key: str, device_type_id: str, app_name: str, app_id: str,
                               app_version: str):
        data = {
            "Key": license_key,
            "DeviceTypeID": device_type_id,
            "Name": app_name,
            "Identifier": app_id,
            "Version": app_version
        }

        body = await cls._post(session, f"{cls.url_fragment}/licenses", data=data)

        Settings.device_id = body["DeviceID"]
        Settings.device_token = body["Token"]
        Settings.role_id = body["RoleID"]
        Settings.user_id = body["UserID"]

        return body
