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
        """
        Retrieve information related to the current organization account.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
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
        """
        Update current organization's account general information.

        :param session: The aiohttp ClientSession to use.
        :param org_name: The new name of the organization.
        :param org_id: The new identifier of the organization.
        :param contact_name: The new contact name.
        :param contact_email: The new contact email.
        :param logo: The new logo (binary data).
        :return: The response from the API.
        """
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
        """
        Retrieves a list of users in the current organization.

        :param session: The aiohttp ClientSession to use.
        :param start_date: Filter by account creation start date (YYYY-MM-DD).
        :param end_date: Filter by account creation end date (YYYY-MM-DD).
        :param email: Filter by User's email address.
        :param role_id: Filter by user's Role ID.
        :param gender: Filter by User's Gender.
        :param region: Filter by Region.
        :param limit: The number of users to pull from the list.
        :param offset: Offset of the results to start at.
        :return: The response from the API.
        """
        params = {
            "Date": start_date,
            "EndDate": end_date,
            "Username": email,
            "RoleID": role_id,
            "Gender": gender,
            "Region": region.lower(),
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
        """
        Create a user within the organization.

        :param session: The aiohttp ClientSession to use.
        :param first_name: The user's first name.
        :param last_name: The user's last name.
        :param email: The user's email address.
        :param gender: The user's gender.
        :param date_of_birth: The user's date of birth.
        :param role_id: The user's role ID.
        :return: The response from the API.
        """
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
        """
        Exchange a license key for a Device Token Pair.

        :param session: The aiohttp ClientSession to use.
        :param license_key: The license key.
        :param device_type_id: The device type ID.
        :param app_name: The application name.
        :param app_id: The application identifier.
        :param app_version: The application version.
        :param token_expires_in_seconds: The seconds for which the access token will be valid for.
        :param token_subject: The token subject.
        :param refresh_token_expires_in_sec: The seconds for which the refresh token will be valid for.
        :return: The response from the API.
        """
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
        """
        Decommission a registered device.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
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
        """
        Retrieves an Organization logo.

        :param session: The aiohttp ClientSession to use.
        :param org_id: The Organization ID.
        :return: The response from the API.
        """
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
        """
        Retrieves all measurements across an Organization.

        :param session: The aiohttp ClientSession to use.
        :param date: Measurement creation start date (YYYY-MM-DD).
        :param end_date: Measurement creation end date (YYYY-MM-DD).
        :param user_profile_id: Filter by a Profile ID.
        :param user_profile_name: Filter by a Profile Name.
        :param study_id: Filter by Study ID.
        :param status_id: Filter by measurement Status ID.
        :param email: Filter by User's email address or phone number.
        :param partner_id: Filter by Partner ID.
        :param mode: Filter by Mode.
        :param region: Filter by Region.
        :param limit: The number of measurements to pull from the list.
        :param offset: Offset to specify the start of the count.
        :return: The response from the API.
        """
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
        """
        Retrieves a measurement across the Organization.

        :param session: The aiohttp ClientSession to use.
        :param measurement_id: The measurement UUID.
        :param expand: Whether to expand the results.
        :return: The response from the API.
        """
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
        """
        Retrieves Profiles across the Organization.

        :param session: The aiohttp ClientSession to use.
        :param date: Profile creation start date (YYYY-MM-DD).
        :param end_date: Profile creation end date (YYYY-MM-DD).
        :param owner_email: Filter by User's email address or phone number.
        :param user_profile_name: Filter by Profile Name.
        :param status_id: Filter by Profile Status ID.
        :param limit: The number of profiles to pull from the list.
        :param offset: Offset to specify the start of the count.
        :return: The response from the API.
        """
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
        """
        Retrieves a Profile across the Organization.

        :param session: The aiohttp ClientSession to use.
        :param profile_id: The Profile UUID.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/profiles/{profile_id}", **kwargs)

    @classmethod
    async def update_profile(cls,
                             session: aiohttp.ClientSession,
                             profile_id: str,
                             name: str = "",
                             email: str = "",
                             status: str = "",
                             **kwargs: Any) -> Any:
        """
        Updates a Profile from the Organization.

        :param session: The aiohttp ClientSession to use.
        :param profile_id: The Profile ID to perform the update on.
        :param name: The new name.
        :param email: The new email.
        :param status: The new status.
        :return: The response from the API.
        """
        data = {
            "Name": name,
            "Email": email,
            "Status": status,
        }

        return await cls._patch(session, f"{cls.url_fragment}/profiles/{profile_id}", data=data, **kwargs)

    @classmethod
    async def retrieve_user(cls, session: aiohttp.ClientSession, user_id: str, **kwargs: Any) -> Any:
        """
        Retrieves a User from the Organization.

        :param session: The aiohttp ClientSession to use.
        :param user_id: The user account ID.
        :return: The response from the API.
        """
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
        """
        Updates a User from the Organization.

        :param session: The aiohttp ClientSession to use.
        :param user_id: The user account ID.
        :param first_name: The new first name.
        :param last_name: The new last name.
        :param gender: The new gender.
        :param date_of_birth: The new date of birth.
        :param height_cm: The new height in cm.
        :param weight_kg: The new weight in kg.
        :return: The response from the API.
        """
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
        """
        Removes a User from the Organization.

        :param session: The aiohttp ClientSession to use.
        :param user_id: The user account ID.
        :return: The response from the API.
        """
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
        """
        Login and obtain a User Token Pair.

        :param session: The aiohttp ClientSession to use.
        :param email: The user's email.
        :param password: The user's password.
        :param org_id: The organization identifier.
        :param mfa_token: The MFA token (if enabled).
        :param token_expires_in_sec: The seconds for which the access token will be valid for.
        :param refresh_token_expires_in_sec: The seconds for which the refresh token will be valid for.
        :return: The response from the API.
        """
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
        """
        Authenticate via WebSocket using a token.

        :param ws: The WebSocket connection.
        :param request_id: The request ID.
        """
        action_id = "0718"

        request = {
            "Token":  Settings.user_token if Settings.user_token else Settings.device_token,
        }

        ws_request = f"{action_id:4}{request_id:10}{json.dumps(request)}"

        await ws.send_str(ws_request)

    @classmethod
    async def delete_all_measurements(cls, session: aiohttp.ClientSession, org_id: str, **kwargs: Any) -> Any:
        """
        Delete all measurements for an organization.

        :param session: The aiohttp ClientSession to use.
        :param org_id: The organization ID.
        :return: The response from the API.
        """
        warnings.warn(f"{cls.delete_all_measurements.__qualname__} is deprecated and will be removed.",
                      DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{org_id}/measurements", **kwargs)

    @classmethod
    async def delete_measurements_by_partnerid(cls, session: aiohttp.ClientSession, org_id: str, partner_id: str,
                                               **kwargs: Any) -> Any:
        """
        Delete measurements by partner ID.

        :param session: The aiohttp ClientSession to use.
        :param org_id: The organization ID.
        :param partner_id: The partner ID.
        :return: The response from the API.
        """
        warnings.warn(f"{cls.delete_measurements_by_partnerid.__qualname__} is deprecated and will be removed.",
                      DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{org_id}/partners/{partner_id}/measurements", **kwargs)
