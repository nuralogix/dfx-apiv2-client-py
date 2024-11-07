# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

import base64
import json
import warnings
from typing import Any, Union

import aiohttp

from .Base import Base
from .Settings import Settings


class Organizations(Base):
    url_fragment = "organizations"

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._get(session, cls.url_fragment, **kwargs)

    @classmethod
    async def update(cls,
                     session: aiohttp.ClientSession,
                     org_name: str = "",
                     org_id: str = "",
                     contact_name: str = "",
                     contact_email: str = "",
                     logo: Union[None, bytes, bytearray, memoryview] = None,
                     **kwargs: Any) -> Any:
        data = {
            "Name": org_name,
            "Identifier": org_id,
            "Contact": contact_name,
            "Email": contact_email,
            "Logo": base64.standard_b64encode(logo).decode('ascii') if logo is not None else logo,
        }
        return await cls._patch(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def list_users(cls,
                         session: aiohttp.ClientSession,
                         start_date: str = "",
                         end_date: str = "",
                         email: str = "",
                         role_id: str = "",
                         gender: str = "",
                         region: str = "",
                         limit: int = 25,
                         offset: int = 0,
                         **kwargs: Any) -> Any:
        params = {
            "Date": start_date,
            "EndDate": end_date,
            "Username": email,
            "RoleID": role_id,
            "Gender": gender,
            "Region": region,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, f"{cls.url_fragment}/users", params=params, **kwargs)

    @classmethod
    async def create_user(cls,
                          session: aiohttp.ClientSession,
                          first_name: str,
                          last_name: str,
                          email: str,
                          gender: str,
                          date_of_birth: str,
                          role_id: str,
                          **kwargs: Any) -> Any:
        data = {
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "Gender": gender,
            "DateOfBirth": date_of_birth,
            "RoleID": role_id
        }

        return await cls._post(session, f"{cls.url_fragment}/users", data=data, **kwargs)

    @classmethod
    async def register_license(cls,
                               session: aiohttp.ClientSession,
                               license_key: str,
                               device_type_id: str,
                               app_name: str,
                               app_id: str,
                               app_version: str,
                               token_expires_in_seconds: int = 0,
                               token_subject: str = "",
                               refresh_token_expires_in_sec: int = 0,
                               **kwargs: Any) -> Any:
        data = {
            "Key": license_key,
            "DeviceTypeID": device_type_id,  # TODO: Describe list of allowed values here and in params below
            "Name": app_name,
            "Identifier": app_id,
            "Version": app_version[:20],
            "TokenSubject": token_subject,
            "TokenExpiresIn": token_expires_in_seconds if token_expires_in_seconds > 0 else 86400,
            "RefreshTokenExpiresIn": refresh_token_expires_in_sec if refresh_token_expires_in_sec > 0 else 2592000
        }

        status, body = await cls._post(session, f"{cls.url_fragment}/licenses", data=data, **kwargs)

        if status < 400:
            Settings.device_id = body["DeviceID"]
            Settings.device_token = body["Token"]
            Settings.device_refresh_token = body["RefreshToken"]
            Settings.role_id = body["RoleID"]
            Settings.user_id = body["UserID"]  # TODO: Verify why returned

        return status, body

    @classmethod
    async def unregister_license(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        status, body = await cls._delete(session, f"{cls.url_fragment}/licenses", **kwargs)

        if status < 400:
            Settings.device_token = ""
            Settings.device_id = ""
            Settings.role_id = ""
            Settings.user_id = ""
            Settings.device_refresh_token = ""

        return status, body

    @classmethod
    async def retrieve_logo(cls, session: aiohttp.ClientSession, org_id: str, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{org_id}/logo", **kwargs)

    @classmethod
    async def list_measurements(cls,
                                session: aiohttp.ClientSession,
                                date: str = "",
                                end_date: str = "",
                                user_profile_id: str = "",
                                user_profile_name: str = "",
                                study_id: str = "",
                                status_id: str = "",
                                email: str = "",
                                partner_id: str = "",
                                mode: str = "",
                                region: str = "",
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
            "UserName": email,
            "PartnerID": partner_id,
            "Mode": mode.upper(),
            "Region": region.lower(),
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, f"{cls.url_fragment}/measurements", params=params, **kwargs)

    @classmethod
    async def retrieve_measurement(cls,
                                   session: aiohttp.ClientSession,
                                   measurement_id: str,
                                   expand: bool = True,
                                   **kwargs: Any) -> Any:
        params = {}
        if expand:
            params["ExpandResults"] = "true"
        return await cls._get(session, f"{cls.url_fragment}/measurements/{measurement_id}", params=params, **kwargs)

    @classmethod
    async def list_profiles(
        cls,
        session: aiohttp.ClientSession,
        date: str = "",
        end_date: str = "",
        owner_email: str = "",
        user_profile_name: str = "",
        status_id: str = "",
        limit: int = 25,
        offset: int = 0,
        **kwargs: Any,
    ) -> Any:
        params = {
            "Date": date,
            "EndDate": end_date,
            "OwnerUser": owner_email,
            "UserProfileName": user_profile_name,
            "StatusID": status_id,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, f"{cls.url_fragment}/profiles", params=params, **kwargs)

    @classmethod
    async def retrieve_profile(cls, session: aiohttp.ClientSession, profile_id: str, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/profiles/{profile_id}", **kwargs)

    @classmethod
    async def update_profile(cls,
                             session: aiohttp.ClientSession,
                             profile_id: str,
                             name: str = "",
                             email: str = "",
                             status: str = "",
                             **kwargs: Any) -> Any:
        data = {
            "Name": name,
            "Email": email,
            "Status": status,
        }

        return await cls._patch(session, f"{cls.url_fragment}/profiles/{profile_id}", data=data, **kwargs)

    @classmethod
    async def retrieve_user(cls, session: aiohttp.ClientSession, user_id: str, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/users/{user_id}", **kwargs)

    @classmethod
    async def update_user(cls,
                          session: aiohttp.ClientSession,
                          user_id: str,
                          first_name: str = "",
                          last_name: str = "",
                          gender: str = "",
                          date_of_birth: str = "",
                          height_cm: Union[str, int] = "",
                          weight_kg: Union[str, int] = "",
                          **kwargs: Any) -> Any:
        data = {
            "FirstName": first_name,
            "LastName": last_name,
            "Gender": gender,
            "DateOfBirth": date_of_birth,
            "HeightCm": str(height_cm),
            "WeightKg": str(weight_kg),
        }

        return await cls._patch(session, f"{cls.url_fragment}/users/{user_id}", data=data, **kwargs)

    @classmethod
    async def remove_user(cls, session: aiohttp.ClientSession, user_id: str, **kwargs: Any) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/users/{user_id}", **kwargs)

    @classmethod
    async def login(cls,
                    session: aiohttp.ClientSession,
                    email: str,
                    password: str,
                    org_id: str,
                    mfa_token: str = "",
                    token_expires_in_sec: int = 0,
                    refresh_token_expires_in_sec: int = 0,
                    **kwargs: Any) -> Any:
        data = {
            "Email": email,
            "Password": password,
            "Identifier": org_id,
            "MFAToken": mfa_token,
            "TokenExpiresIn": token_expires_in_sec if token_expires_in_sec > 0 else 86400,
            "RefreshTokenExpiresIn": refresh_token_expires_in_sec if refresh_token_expires_in_sec > 0 else 2592000
        }

        status, body = await cls._post(session, f"{cls.url_fragment}/auth", data=data, **kwargs)

        if status < 400:
            Settings.user_token = body["Token"]
            Settings.user_refresh_token = body["RefreshToken"]

        return status, body

    @classmethod
    async def ws_auth_with_token(cls, ws: aiohttp.ClientWebSocketResponse, request_id: Union[str, int]) -> None:
        action_id = "0718"

        request = {
            "Token":  Settings.user_token if Settings.user_token else Settings.device_token,
        }

        ws_request = f"{action_id:4}{request_id:10}{json.dumps(request)}"

        await ws.send_str(ws_request)

    @classmethod
    async def delete_all_measurements(cls, session: aiohttp.ClientSession, org_id: str, **kwargs: Any) -> Any:
        warnings.warn(f"{cls.delete_all_measurements.__qualname__} is deprecated and will be removed.",
                      DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{org_id}/measurements", **kwargs)

    @classmethod
    async def delete_measurements_by_partnerid(cls, session: aiohttp.ClientSession, org_id: str, partner_id: str,
                                               **kwargs: Any) -> Any:
        warnings.warn(f"{cls.delete_measurements_by_partnerid.__qualname__} is deprecated and will be removed.",
                      DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{org_id}/partners/{partner_id}/measurements", **kwargs)
