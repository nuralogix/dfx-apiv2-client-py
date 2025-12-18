# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

from typing import Any, Optional

import aiohttp

from .Base import Base
from .Settings import Settings


class Auths(Base):
    url_fragment = "auths"

    @classmethod
    async def request_password_reset_email(cls, session: aiohttp.ClientSession, email: str, org_id: str,
                                           **kwargs: Any) -> Any:
        """
        Request to send a password reset link to the user's email.

        :param session: The aiohttp ClientSession to use.
        :param email: The email address of the user.
        :param org_id: The organization identifier.
        :return: The response from the API.
        """
        data = {
            "Email": email,
            "Identifier": org_id,
        }
        return await cls._patch(session, f"{cls.url_fragment}/users/reset", data=data, **kwargs)

    @classmethod
    async def request_login_code(cls, session: aiohttp.ClientSession, phone_number: str, org_id: str,
                                 **kwargs: Any) -> Any:
        """
        Request a login code for phone number authentication.

        :param session: The aiohttp ClientSession to use.
        :param phone_number: The phone number to send the code to.
        :param org_id: The organization identifier.
        :return: The response from the API.
        """
        data = {
            "PhoneNumber": phone_number,
            "Identifier": org_id,
        }
        return await cls._post(session, f"{cls.url_fragment}/users/code", data=data, **kwargs)

    @classmethod
    async def renew_token(cls,
                          session: aiohttp.ClientSession,
                          token: str,
                          refresh_token: str,
                          refresh_token_expires_sec: Optional[int] = None,
                          **kwargs: Any) -> Any:
        """
        Renew an access and refresh token pair.

        :param session: The aiohttp ClientSession to use.
        :param token: The current access token.
        :param refresh_token: The current refresh token.
        :param refresh_token_expires_sec: Optional expiration time for the new refresh token in seconds.
        :return: The response from the API containing the new token pair.
        """
        data = {
            "Token": token,
            "RefreshToken": refresh_token,
            "RefreshTokenExpiresIn": int(refresh_token_expires_sec) if refresh_token_expires_sec is not None else None
        }
        return await cls._post(session, f"{cls.url_fragment}/renew", data=data, **kwargs)

    @classmethod
    async def renew_user_token(cls,
                               session: aiohttp.ClientSession,
                               refresh_token_expires_sec: Optional[int] = None,
                               **kwargs: Any) -> Any:
        """
        Renew the current user's token pair stored in Settings.

        Updates Settings.user_token and Settings.user_refresh_token if successful.

        :param session: The aiohttp ClientSession to use.
        :param refresh_token_expires_sec: Optional expiration time for the new refresh token in seconds.
        :return: The status code and response body.
        """
        status, body = await cls.renew_token(session, Settings.user_token, Settings.user_refresh_token,
                                             refresh_token_expires_sec, **kwargs)

        if status < 400:
            Settings.user_token = body["Token"]
            Settings.user_refresh_token = body["RefreshToken"]

        return status, body

    @classmethod
    async def renew_device_token(cls,
                                 session: aiohttp.ClientSession,
                                 refresh_token_expires_sec: Optional[int] = None,
                                 **kwargs: Any) -> Any:
        """
        Renew the current device's token pair stored in Settings.

        Updates Settings.device_token and Settings.device_refresh_token if successful.

        :param session: The aiohttp ClientSession to use.
        :param refresh_token_expires_sec: Optional expiration time for the new refresh token in seconds.
        :return: The status code and response body.
        """
        status, body = await cls.renew_token(session, Settings.device_token, Settings.device_refresh_token,
                                             refresh_token_expires_sec, **kwargs)

        if status < 400:
            Settings.device_token = body["Token"]
            Settings.device_refresh_token = body["RefreshToken"]

        return status, body

    @classmethod
    async def request_child_token(cls,
                                  session: aiohttp.ClientSession,
                                  token: str,
                                  refresh_token: str,
                                  token_expires_sec: Optional[int] = None,
                                  **kwargs: Any) -> Any:
        """
        Generate a child token without expiring the input token.

        :param session: The aiohttp ClientSession to use.
        :param token: The parent access token.
        :param refresh_token: The parent refresh token.
        :param token_expires_sec: Optional expiration time for the child token in seconds.
        :return: The response from the API containing the child token.
        """
        data = {
            "Token": token,
            "RefreshToken": refresh_token,
            "expiryInSec": int(token_expires_sec) if token_expires_sec is not None else None,
        }
        return await cls._post(session, f"{cls.url_fragment}/generateToken", data=data, **kwargs)
