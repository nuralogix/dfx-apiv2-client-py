# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

from typing import Any

import aiohttp

from .Base import Base


class Profiles(Base):
    url_fragment = "users/profiles"

    @classmethod
    async def create(cls, session: aiohttp.ClientSession, profile_name: str, email: str, **kwargs: Any) -> Any:
        """
        Create a user profile.

        :param session: The aiohttp ClientSession to use.
        :param profile_name: The name of the profile.
        :param email: The email associated with the profile.
        :return: The response from the API.
        """
        data = {
            "Name": profile_name,
            "Email": email,
        }

        status, body = await cls._post(session, cls.url_fragment, data=data, **kwargs)

        return status, body

    @classmethod
    async def update(cls, session: aiohttp.ClientSession, profile_id: str, profile_name: str, profile_email: str,
                     status: str, **kwargs: Any) -> Any:
        """
        Update a specific user profile.

        :param session: The aiohttp ClientSession to use.
        :param profile_id: The ID of the profile to update.
        :param profile_name: The new name of the profile.
        :param profile_email: The new email of the profile.
        :param status: The new status of the profile (ACTIVE or INACTIVE).
        :return: The response from the API.
        """
        data = {
            "Name": profile_name,
            "Email": profile_email,
            "Status": status,
        }
        return await cls._patch(session, f"{cls.url_fragment}/{profile_id}", data=data, **kwargs)

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, profile_id: str, **kwargs: Any) -> Any:
        """
        Remove a user profile.

        :param session: The aiohttp ClientSession to use.
        :param profile_id: The ID of the profile to remove.
        :return: The response from the API.
        """
        return await cls._delete(session, f"{cls.url_fragment}/{profile_id}", **kwargs)

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, profile_id: str, **kwargs: Any) -> Any:
        """
        Retrieve a single user profile.

        :param session: The aiohttp ClientSession to use.
        :param profile_id: The ID of the profile to retrieve.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/{profile_id}", **kwargs)

    @classmethod
    async def list(cls,
                   session: aiohttp.ClientSession,
                   profile_name: str = "",
                   status: str = "",
                   limit: int = 25,
                   offset: int = 0,
                   **kwargs: Any) -> Any:
        """
        List profiles managed under the current user account.

        :param session: The aiohttp ClientSession to use.
        :param profile_name: Filter by profile name.
        :param status: Filter by profile status.
        :param limit: The number of results to return.
        :param offset: The offset to start returning results from.
        :return: The response from the API.
        """
        params = {
            "UserProfileName": profile_name,
            "Status": status,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, cls.url_fragment, params=params, **kwargs)

    @classmethod
    async def list_by_user(cls,
                           session: aiohttp.ClientSession,
                           user_id: str = "",
                           profile_name: str = "",
                           status: str = "",
                           limit: int = 25,
                           offset: int = 0,
                           **kwargs: Any) -> Any:
        """
        List profiles managed under a specific user account.

        :param session: The aiohttp ClientSession to use.
        :param user_id: The ID of the user to list profiles for.
        :param profile_name: Filter by profile name.
        :param status: Filter by profile status.
        :param limit: The number of results to return.
        :param offset: The offset to start returning results from.
        :return: The response from the API.
        """
        params = {
            "UserProfileName": profile_name,
            "Status": status,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, f"users/{user_id}/profiles", params=params, **kwargs)
