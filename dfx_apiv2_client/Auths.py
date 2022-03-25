# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

from typing import Any

import aiohttp

from .Base import Base
from .Settings import Settings


class Auths(Base):
    url_fragment = "auths"

    @classmethod
    async def request_password_reset_email(cls, session: aiohttp.ClientSession, email: str, org_id: str,
                                           **kwargs: Any) -> Any:
        data = {
            "Email": email,
            "Identifier": org_id,
        }
        return await cls._patch(session, f"{cls.url_fragment}/users/reset", data=data, **kwargs)

    @classmethod
    async def request_login_code(cls, session: aiohttp.ClientSession, phone_number: str, org_id: str,
                                 **kwargs: Any) -> Any:
        data = {
            "PhoneNumber": phone_number,
            "Identifier": org_id,
        }
        return await cls._patch(session, f"{cls.url_fragment}/users/code", data=data, **kwargs)

    @classmethod
    async def _renew_token(cls, session: aiohttp.ClientSession, token: str, refresh_token: str, **kwargs: Any) -> Any:
        data = {
            "Token": token,
            "RefreshToken": refresh_token,
        }
        return cls._post(session, f"{cls.url_fragment}/renew", data=data, **kwargs)

    @classmethod
    async def renew_user_token(cls, session: aiohttp.ClientSession, user_token: str, user_refresh_token: str,
                               **kwargs: Any) -> Any:
        body, status = await cls._renew_token(session, user_token, user_refresh_token, **kwargs)

        if status < 400:
            Settings.user_token = body["Token"]
            Settings.user_refresh_token = body["RefreshToken"]

        return status, body

    @classmethod
    async def renew_device_token(cls, session: aiohttp.ClientSession, device_token: str, device_refresh_token: str,
                                 **kwargs: Any) -> Any:
        body, status = await cls._renew_token(session, device_token, device_refresh_token, **kwargs)

        if status < 400:
            Settings.user_token = body["Token"]
            Settings.user_refresh_token = body["RefreshToken"]

        return status, body
