# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

from typing import Any

import aiohttp

from .Base import Base


class Profiles(Base):
    url_fragment = "users/profiles"

    @classmethod
    async def create(cls, session: aiohttp.ClientSession, profile_name: str, email: str, **kwargs: Any) -> Any:
        data = {
            "Name": profile_name,
            "Email": email,
        }

        status, body = await cls._post(session, cls.url_fragment, data=data, **kwargs)

        return status, body

    @classmethod
    async def update(cls, session: aiohttp.ClientSession, profile_id: str, profile_name: str, profile_email: str, status: str,
                     **kwargs: Any) -> Any:
        data = {
            "Name": profile_name,
            "Email": profile_email,
            "Status": status,
        }
        return await cls._patch(session, f"{cls.url_fragment}/{profile_id}", data=data, **kwargs)

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, profile_id: str, **kwargs: Any) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/{profile_id}", **kwargs)

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, profile_id: str, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{profile_id}", **kwargs)

    @classmethod
    async def list(cls,
                   session: aiohttp.ClientSession,
                   profile_name: str = "",
                   status: str = "",
                   limit: int = 25,
                   offset: int = 0,
                   **kwargs: Any) -> Any:
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
        params = {
            "UserProfileName": profile_name,
            "Status": status,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, f"users/{user_id}/profiles", params=params, **kwargs)
