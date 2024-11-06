# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

import warnings
from typing import Any, Optional

import aiohttp

from .Base import Base


class Studies(Base):
    url_fragment = "studies"

    @classmethod
    async def types(cls, session: aiohttp.ClientSession, status: str, **kwargs: Any) -> Any:
        params = {
            "StatusID": status,
        }
        return await cls._get(session, f"{cls.url_fragment}/types", params=params, **kwargs)

    @classmethod
    async def list_templates(cls,
                             session: aiohttp.ClientSession,
                             status: str,
                             type_: str,
                             sort_order: str = "",
                             sort_key: str = "",
                             limit: int = 0,
                             offset: int = 0,
                             **kwargs: Any) -> Any:
        params = {
            "Status": status,
            "Type": type_,
            "SortOrder": sort_order.upper(),
            "SortBy": sort_key,
            "Limit": limit,
            "Offset": offset,
        }
        return await cls._get(session, f"{cls.url_fragment}/templates", params=params, **kwargs)

    @classmethod
    async def create(cls, session: aiohttp.ClientSession, study_name: str, description: str, study_template_id: str,
                     config: dict, **kwargs: Any) -> Any:
        data = {
            "Name": study_name,
            "Description": description,
            "StudyTemplateID": study_template_id,
            "Config": config,
        }

        return await cls._post(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def update(cls,
                     session: aiohttp.ClientSession,
                     study_id: str,
                     study_name: str = "",
                     description: str = "",
                     status: str = "",
                     config: Optional[dict] = None,
                     **kwargs: Any) -> Any:
        data = {
            "Name": study_name,
            "StatusID": status.upper(),
            "Description": description,
            "Config": config,
        }

        return await cls._patch(session, f"{cls.url_fragment}/{study_id}", data=data, **kwargs)

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, study_id: str, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{study_id}", **kwargs)

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, study_id: str, **kwargs: Any) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/{study_id}", **kwargs)

    @classmethod
    async def list(cls,
                   session: aiohttp.ClientSession,
                   date: str = "",
                   end_date: str = "",
                   study_name: str = "",
                   status: str = "",
                   limit: int = 0,
                   offset: int = 0,
                   **kwargs: Any) -> Any:
        params = {
            "Date": date,
            "EndDate": end_date,
            "Name": study_name,
            "StatusID": status.upper(),
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, cls.url_fragment, params=params, **kwargs)

    @classmethod
    async def retrieve_sdk_config_data(cls, session: aiohttp.ClientSession, study_id: str, sdk_id: str,
                                       current_hash: str, **kwargs: Any) -> Any:
        data = {
            "StudyID": study_id,
            "SDKID": sdk_id,
            "MD5Hash": current_hash,
        }

        return await cls._post(session, f"{cls.url_fragment}/sdkconfig", data=data, **kwargs)

    @classmethod
    async def delete_study_measurements(cls, session: aiohttp.ClientSession, study_id: str, **kwargs: Any) -> Any:
        warnings.warn(f"{cls.delete_study_measurements.__qualname__} is deprecated and will be removed.",
                      DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{study_id}/measurements", **kwargs)
