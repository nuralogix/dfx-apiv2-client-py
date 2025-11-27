# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

from typing import Any

import aiohttp

from .Base import Base


class Licenses(Base):
    url_fragment = "licenses"

    @classmethod
    async def list(cls,
                   session: aiohttp.ClientSession,
                   date: str = "",
                   end_date: str = "",
                   status_id: str = "",
                   license_type_id: str = "",
                   license_type: str = "",
                   limit: int = 25,
                   offset: int = 0,
                   **kwargs: Any) -> Any:
        """
        List licenses associated with the organization.

        :param session: The aiohttp ClientSession to use.
        :param date: Filter by date (YYYY-MM-DD).
        :param end_date: Filter by end date (YYYY-MM-DD).
        :param status_id: Filter by status ID.
        :param license_type_id: Filter by license type ID.
        :param license_type: Filter by license type.
        :param limit: The number of results to return.
        :param offset: The offset to start returning results from.
        :return: The response from the API.
        """
        params = {
            "StatusID": status_id.upper(),
            "LicenseTypeID": license_type_id,
            "LicenseType": license_type,
            "Date": date,
            "EndDate": end_date,
            "Limit": limit,
            "Offset": offset,
        }
        return await cls._get(session, f"{cls.url_fragment}/organization", params=params, **kwargs)

    @classmethod
    async def get(cls, session: aiohttp.ClientSession, license_id: str = "", **kwargs: Any) -> Any:
        """
        Retrieve a specific license by its ID.

        :param session: The aiohttp ClientSession to use.
        :param license_id: The ID of the license to retrieve.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/organization/{license_id}", **kwargs)
