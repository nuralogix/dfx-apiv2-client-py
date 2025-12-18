# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

import warnings
from typing import Any, Union

import aiohttp

from .Auths import Auths  # Just for __qualname__
from .Base import Base
from .Settings import Settings


class Users(Base):
    url_fragment = "users"

    @classmethod
    async def create(cls,
                     session: aiohttp.ClientSession,
                     first_name: str,
                     last_name: str,
                     email: str,
                     password: str,
                     phone_number: str,
                     gender: str,
                     date_of_birth: str,
                     height_cm: Union[str, int],
                     weight_kg: Union[str, int],
                     **kwargs: Any) -> Any:
        """
        Creates a new user in the organization.

        :param session: The aiohttp ClientSession to use.
        :param first_name: The user's first name.
        :param last_name: The user's last name.
        :param email: The user's email address.
        :param password: The user's password.
        :param phone_number: The user's phone number.
        :param gender: The user's gender.
        :param date_of_birth: The user's date of birth (YYYY-MM-DD).
        :param height_cm: The user's height in centimeters.
        :param weight_kg: The user's weight in kilograms.
        :return: The response from the API.
        """
        data = {
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "Password": password,
            "PhoneNumber": phone_number,
            "Gender": gender,
            "DateOfBirth": date_of_birth,
            "HeightCm": str(height_cm),
            "WeightKg": str(weight_kg),
        }

        return await cls._post(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def login(cls,
                    session: aiohttp.ClientSession,
                    email: str,
                    password: str,
                    mfa_token: str = "",
                    token_expires_in_sec: int = 0,
                    refresh_token_expires_in_sec: int = 0,
                    **kwargs: Any) -> Any:
        """
        Logs a user into a new session using Email and Password.

        :param session: The aiohttp ClientSession to use.
        :param email: The user's email.
        :param password: The user's password.
        :param mfa_token: The MFA token (if enabled).
        :param token_expires_in_sec: The seconds for which the access token will be valid for.
        :param refresh_token_expires_in_sec: The seconds for which the refresh token will be valid for.
        :return: The response from the API.
        """
        data = {
            "Email": email,
            "Password": password,
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
    async def request_phone_login_code(cls, session: aiohttp.ClientSession, org_key: str, phone_number: str,
                                       **kwargs: Any) -> Any:
        """
        Request a login code for a User account created with a Phone Number.

        :param session: The aiohttp ClientSession to use.
        :param org_key: The Organization Key.
        :param phone_number: The user's phone number.
        :return: The response from the API.
        """
        warnings.warn(
            f"{cls.request_phone_login_code.__qualname__} is deprecated. "
            f"Please use {Auths.request_login_code.__qualname__} instead.", DeprecationWarning)
        return await cls._get(session, f"{cls.url_fragment}/auth/code/{org_key}/{phone_number}", **kwargs)

    @classmethod
    async def login_with_phone_code(cls,
                                    session: aiohttp.ClientSession,
                                    org_key: str,
                                    phone_number: str,
                                    login_code: str,
                                    token_expires_in_sec: int = 0,
                                    refresh_token_expires_in_sec: int = 0,
                                    **kwargs: Any) -> Any:
        """
        Use previously requested 6-digit code to login into a new session.

        :param session: The aiohttp ClientSession to use.
        :param org_key: The Organization Key.
        :param phone_number: The user's phone number.
        :param login_code: The 6-digit login code.
        :param token_expires_in_sec: The seconds for which the access token will be valid for.
        :param refresh_token_expires_in_sec: The seconds for which the refresh token will be valid for.
        :return: The response from the API.
        """
        data = {
            "LoginCode": login_code,
            "PhoneNumber": phone_number,
            "OrgKey": org_key,
            "TokenExpiresIn": token_expires_in_sec if token_expires_in_sec > 0 else 86400,
            "RefreshTokenExpiresIn": refresh_token_expires_in_sec if refresh_token_expires_in_sec > 0 else 2592000
        }

        status, body = await cls._post(session, f"{cls.url_fragment}/auth/code", data=data, **kwargs)

        if status < 400:
            Settings.user_token = body["Token"]
            Settings.user_refresh_token = body["RefreshToken"]

        return body

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        """
        Retrieves User account information based on the provided User Token.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
        return await cls._get(session, cls.url_fragment, **kwargs)

    @classmethod
    async def update(cls,
                     session: aiohttp.ClientSession,
                     first_name: str,
                     last_name: str,
                     email: str,
                     password: str,
                     phone_number: str,
                     gender: str,
                     date_of_birth: str,
                     height_cm: Union[str, int],
                     weight_kg: Union[str, int],
                     **kwargs: Any) -> Any:
        """
        Updates a user's account information with new details.

        :param session: The aiohttp ClientSession to use.
        :param first_name: The user's first name.
        :param last_name: The user's last name.
        :param email: The user's email address.
        :param password: The user's password.
        :param phone_number: The user's phone number.
        :param gender: The user's gender.
        :param date_of_birth: The user's date of birth.
        :param height_cm: The user's height in centimeters.
        :param weight_kg: The user's weight in kilograms.
        :return: The response from the API.
        """
        data = {
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "Password": password,
            "PhoneNumber": phone_number,
            "Gender": gender,
            "DateOfBirth": date_of_birth,
            "HeightCm": str(height_cm),
            "WeightKg": str(weight_kg),
        }

        return await cls._patch(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def create_mfa_secret(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        """
        Creates a base32 secret, url and a QR code for 2FA.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
        return await cls._post(session, f"{cls.url_fragment}/mfa/secret", data=None, **kwargs)

    @classmethod
    async def enable_mfa(cls, session: aiohttp.ClientSession, mfa_secret: str, mfa_token: str, **kwargs: Any) -> Any:
        """
        Enables 2FA for logged in user using an MFASecret and MFAToken.

        :param session: The aiohttp ClientSession to use.
        :param mfa_secret: The MFA secret.
        :param mfa_token: The MFA token.
        :return: The response from the API.
        """
        data = {
            "MFASecret": mfa_secret,
            "MFAToken": mfa_token,
        }

        return await cls._post(session, f"{cls.url_fragment}/mfa", data=data, **kwargs)

    @classmethod
    async def disable_mfa_by_userid(cls, session: aiohttp.ClientSession, user_id: str, **kwargs: Any) -> Any:
        """
        Disables 2FA for user by its ID.

        :param session: The aiohttp ClientSession to use.
        :param user_id: The user's ID.
        :return: The response from the API.
        """
        return await cls._delete(session, f"{cls.url_fragment}/{user_id}/mfa", **kwargs)

    @classmethod
    async def disable_mfa(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        """
        Disables 2FA for logged in user.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
        return await cls._delete(session, f"{cls.url_fragment}/mfa", **kwargs)

    @classmethod
    async def retrieve_user_role(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        """
        Retrieves User's Role.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/role", **kwargs)

    @classmethod
    async def send_password_reset_request(cls, session: aiohttp.ClientSession, email: str, org_id: str,
                                          **kwargs: Any) -> Any:
        """
        Dispatches a password reset request email to the user.

        :param session: The aiohttp ClientSession to use.
        :param email: The user's email.
        :param org_id: The organization identifier.
        :return: The response from the API.
        """
        warnings.warn(
            f"{cls.send_password_reset_request.__qualname__} is deprecated. "
            f"Please use {Auths.request_password_reset_email.__qualname__} instead.", DeprecationWarning)
        data = {
            "Email": email,
            "Identifier": org_id,
        }

        return await cls._patch(session, f"{cls.url_fragment}/sendreset", data=data, **kwargs)

    @classmethod
    async def reset_password(cls, session: aiohttp.ClientSession, reset_token: str, new_password: str,
                             **kwargs: Any) -> Any:
        """
        Resets the user's password using a reset token.

        :param session: The aiohttp ClientSession to use.
        :param reset_token: The password reset token.
        :param new_password: The new password.
        :return: The response from the API.
        """
        warnings.warn(f"{cls.reset_password.__qualname__} is deprecated and will be removed.", DeprecationWarning)

        data = {
            "ResetToken": reset_token,
            "Password": new_password,
        }

        return await cls._patch(session, f"{cls.url_fragment}/reset", data=data, **kwargs)

    @classmethod
    async def send_account_verification_code(cls, session: aiohttp.ClientSession, user_id: str, org_id: str,
                                             **kwargs: Any) -> Any:
        """
        Sends an account verification code to the user's email address.

        :param session: The aiohttp ClientSession to use.
        :param user_id: The user's ID or email address.
        :param org_id: The organization key.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/verificationCode/{user_id}/{org_id}", {}, **kwargs)

    @classmethod
    async def verify_user_account(cls, session: aiohttp.ClientSession, verification_code: str, user_id: str,
                                  **kwargs: Any) -> Any:
        """
        Verifies User's email address.

        :param session: The aiohttp ClientSession to use.
        :param verification_code: The verification code received.
        :param user_id: The user's ID.
        :return: The response from the API.
        """
        data = {
            "VerificationCode": verification_code,
            "ID": user_id,
        }

        return await cls._post(session, f"{cls.url_fragment}/verify", data=data, **kwargs)

    @classmethod
    async def remove(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        """
        Removes the entire user account.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
        return await cls._delete(session, cls.url_fragment, **kwargs)

    @classmethod
    async def delete_measurements_by_userid(cls, session: aiohttp.ClientSession, user_id: str, **kwargs: Any) -> Any:
        """
        Delete measurements associated with a user.

        :param session: The aiohttp ClientSession to use.
        :param user_id: The user's ID.
        :return: The response from the API.
        """
        warnings.warn(f"{cls.delete_measurements_by_userid.__qualname__} is deprecated and will be removed.",
                      DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{user_id}/measurements", **kwargs)

    @classmethod
    async def change_password(cls, session: aiohttp.ClientSession, org_id: str, email: str, password: str,
                              new_password: str, **kwargs: Any) -> Any:
        """
        Change password for already verified user.

        :param session: The aiohttp ClientSession to use.
        :param org_id: The organization identifier.
        :param email: The user's email.
        :param password: The old password.
        :param new_password: The new password.
        :return: The response from the API.
        """
        data = {
            "Identifier": org_id,
            "Email": email,
            "Password": password,
            "NewPassword": new_password,
        }

        return await cls._post(session, f"{cls.url_fragment}/changepassword", data=data, **kwargs)

    @classmethod
    async def renew_token(cls, session: aiohttp.ClientSession, license_key: str, **kwargs: Any) -> Any:
        """
        Renew token.

        :param session: The aiohttp ClientSession to use.
        :param license_key: The license key.
        :return: The response from the API.
        """
        warnings.warn(
            f"{cls.renew_token.__qualname__} is deprecated. Please use {Auths.renew_token.__qualname__} instead.",
            DeprecationWarning)

        data = {
            "Key": license_key,
        }

        return await cls._post(session, f"{cls.url_fragment}/auth/renew", data=data, **kwargs)

    @classmethod
    async def logout(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        """
        Logs user out from all its sessions at once.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
        status, body = await cls._delete(session, f"{cls.url_fragment}/auth", **kwargs)

        if status < 400:
            Settings.user_token = ""
            Settings.user_refresh_token = ""

        return status, body
