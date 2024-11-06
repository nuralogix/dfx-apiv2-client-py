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
        return await cls._get(session, f"{cls.url_fragment}/organization/{license_id}", **kwargs)
