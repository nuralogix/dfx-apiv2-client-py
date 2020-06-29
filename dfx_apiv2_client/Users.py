# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

import datetime
from typing import Any

import aiohttp

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
                     date_of_birth: datetime.date,
                     height_cm: int,
                     weight_kg: int,
                     **kwargs: Any) -> Any:
        data = {
            "FirstName": str(first_name),
            "LastName": str(last_name),
            "Email": str(email).lower(),
            "Password": str(password),
            "PhoneNumber": str(phone_number),
            "Gender": str(gender).lower(),
            "DateOfBirth": date_of_birth.strftime("%Y-%m-%d"),
            "HeightCm": str(height_cm),
            "WeightKg": str(weight_kg),
        }

        return await cls._post(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def login(cls, session: aiohttp.ClientSession, email: str, password: str, **kwargs: Any) -> Any:
        data = {
            "Email": email,
            "Password": password,
        }

        status, body = await cls._post(session, f"{cls.url_fragment}/auth", data=data, **kwargs)

        if status < 400:
            Settings.user_token = body["Token"]

        return status, body

    @classmethod
    async def request_phone_login_code(cls, session: aiohttp.ClientSession, org_key: str, phone_number: str,
                                       **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/auth/code/{org_key}/{phone_number}", **kwargs)

    @classmethod
    async def login_with_phone_code(cls, session: aiohttp.ClientSession, org_key: str, phone_number: str,
                                    login_code: str, **kwargs: Any) -> Any:
        data = {
            "LoginCode": str(login_code),
            "PhoneNumber": str(phone_number),
            "OrgKey": str(org_key),
        }

        body = await cls._post(session, f"{cls.url_fragment}/auth/code", data=data, **kwargs)

        # TODO: Handle raise_for_status == False
        Settings.user_token = body["Token"]

        return body

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
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
                     date_of_birth: datetime.date,
                     height_cm: int,
                     weight_kg: int,
                     **kwargs: Any) -> Any:
        data = {
            "FirstName": str(first_name),
            "LastName": str(last_name),
            "Email": str(email).lower(),
            "Password": str(password),
            "PhoneNumber": str(phone_number),
            "Gender": str(gender).lower(),
            "DateOfBirth": date_of_birth.strftime("%Y-%m-%d"),
            "HeightCm": str(height_cm),
            "WeightKg": str(weight_kg),
        }

        return await cls._patch(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def retrieve_user_role(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/role", **kwargs)

    @classmethod
    async def send_password_reset_request(cls, session: aiohttp.ClientSession, email: str, org_id: str,
                                          **kwargs: Any) -> Any:
        data = {
            "Email": str(email),
            "Identifier": str(org_id),
        }

        return await cls._patch(session, f"{cls.url_fragment}/sendreset", data=data, **kwargs)

    @classmethod
    async def reset_password(cls, session: aiohttp.ClientSession, reset_token: str, new_password: str,
                             **kwargs: Any) -> Any:
        data = {
            "ResetToken": str(reset_token),
            "Password": str(new_password),
        }

        return await cls._patch(session, f"{cls.url_fragment}/reset", data=data, **kwargs)

    @classmethod
    async def send_account_verification_code(cls, session: aiohttp.ClientSession, user_id: str, **kwargs: Any) -> Any:
        return await cls._post(session, f"{cls.url_fragment}/verificationCode/{user_id}", {}, **kwargs)

    @classmethod
    async def verify_user_account(cls, session: aiohttp.ClientSession, verification_code: str, user_id: str,
                                  **kwargs: Any) -> Any:
        data = {
            "VerificationCode": verification_code,
            "ID": user_id,
        }

        return await cls._post(session, f"{cls.url_fragment}/verify", data=data, **kwargs)

    @classmethod
    async def remove(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._delete(session, cls.url_fragment, **kwargs)
