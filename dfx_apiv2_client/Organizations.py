from typing import Any

import aiohttp

from .Base import Base
from .Settings import Settings


class Organizations(Base):
    url_fragment = "organizations"

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession) -> Any:
        return await cls._get(session, cls.url_fragment)

    @classmethod
    async def list_users(
        cls,
        session: aiohttp.ClientSession,
        start_date: str = "",
        end_date: str = "",
        email: str = "",
        role_id: str = "",
        gender: str = "",
        status_id: str = "",
        limit: int = 25,
        offset: int = 0,
    ) -> Any:
        params = {
            "StartDate": start_date,
            "EndDate": end_date,
            "Username": email,
            "RoleID": role_id,
            "Gender": gender,
            "StatusID": status_id,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, f"{cls.url_fragment}/users", params=params)

    @classmethod
    async def create_user(
        cls,
        session: aiohttp.ClientSession,
        first_name: str,
        last_name: str,
        email: str,
        gender: str,
        date_of_birth: str,
        role_id: str,
    ) -> Any:
        data = {
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "Gender": gender,
            "DateOfBirth": date_of_birth,
            "RoleID": role_id
        }

        body = await cls._post(session, f"{cls.url_fragment}/users", data=data)

        return body["ID"]

    @classmethod
    async def register_license(cls, session: aiohttp.ClientSession, license_key: str, device_type_id: str,
                               app_name: str, app_id: str, app_version: str) -> Any:
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
        Settings.user_id = body["UserID"]  # TODO: Why does register license return this

        return body

    @classmethod
    async def unregister_license(cls, session: aiohttp.ClientSession) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/licenses")

    @classmethod
    async def list_measurements(
        cls,
        session: aiohttp.ClientSession,
        date: str = "",
        end_date: str = "",
        user_profile_id: str = "",
        user_profile_name: str = "",
        study_id: str = "",
        status_id: str = "",
        email: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> Any:
        params = {
            "Date": date,
            "EndDate": end_date,
            "UserProfileID": user_profile_id,
            "UserProfileName": user_profile_name,
            "StudyID": study_id,
            "StatusID": status_id,
            "Username": email,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, f"{cls.url_fragment}/measurements", params=params)

    @classmethod
    async def retrieve_measurement(cls,
                                   session: aiohttp.ClientSession,
                                   measurement_id: str,
                                   expand: bool = True) -> Any:
        params = {
            "ExpandResults": "true" if expand else "",
        }
        return await cls._get(session, f"{cls.url_fragment}/measurements/{measurement_id}", params=params)

    @classmethod
    async def list_profiles(
        cls,
        session: aiohttp.ClientSession,
        owner_email: str = "",
        user_profile_name: str = "",
        status_id: str = "",
        created_date: str = "",
        limit: int = 25,
        offset: int = 0,
    ) -> Any:
        params = {
            "OwnerUser": owner_email,
            "UserProfileName": user_profile_name,
            "StatusID": status_id,
            "Created": created_date,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, f"{cls.url_fragment}/profiles", params=params)

    @classmethod
    async def retrieve_profile(cls, session: aiohttp.ClientSession, profile_id: str) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/profiles/{profile_id}")

    @classmethod
    async def update_profile(cls, session: aiohttp.ClientSession, profile_id: str, name: str, email: str,
                             status: str) -> Any:
        data = {
            "Name": str(name),
            "Email": str(email),
            "Status": str(status),
        }

        return await cls._patch(session, f"{cls.url_fragment}/profiles/{profile_id}", data=data)

    @classmethod
    async def retrieve_user(cls, session: aiohttp.ClientSession, user_id: str) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/users/{user_id}")

    @classmethod
    async def update_user(
        cls,
        session: aiohttp.ClientSession,
        user_id: str,
        first_name: str,
        last_name: str,
        gender: str,
        date_of_birth: str,
        height_cm: int,
        weight_kg: int,
    ) -> Any:
        data = {
            "FirstName": str(first_name),
            "LastName": str(last_name),
            "Gender": str(gender),
            "DateOfBirth": str(date_of_birth),
            "HeightCm": str(height_cm),
            "WeightKg": str(weight_kg),
        }

        return await cls._patch(session, f"{cls.url_fragment}/users/{user_id}", data=data)

    @classmethod
    async def remove_user(cls, session: aiohttp.ClientSession, user_id: str) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/users/{user_id}")

    @classmethod
    async def login(cls, session: aiohttp.ClientSession, email: str, password: str, org_identifier: str) -> Any:
        data = {
            "Email": email,
            "Password": password,
            "Identifier": org_identifier,
        }

        body = await cls._post(session, f"{cls.url_fragment}/auth", data=data)

        Settings.user_token = body["Token"]

        return body
