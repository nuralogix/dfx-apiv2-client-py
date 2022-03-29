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
    async def renew_token(cls, session: aiohttp.ClientSession, token: str, refresh_token: str, **kwargs: Any) -> Any:
        data = {
            "Token": token,
            "RefreshToken": refresh_token,
        }
        return await cls._post(session, f"{cls.url_fragment}/renew", data=data, **kwargs)

    @classmethod
    async def renew_user_token(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        status, body = await cls.renew_token(session, Settings.user_token, Settings.user_refresh_token, **kwargs)

        if status < 400:
            Settings.user_token = body["Token"]
            Settings.user_refresh_token = body["RefreshToken"]

        return status, body

    @classmethod
    async def renew_device_token(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        status, body = await cls.renew_token(session, Settings.device_token, Settings.device_refresh_token, **kwargs)

        if status < 400:
            Settings.device_token = body["Token"]
            Settings.device_refresh_token = body["RefreshToken"]

        return status, body
