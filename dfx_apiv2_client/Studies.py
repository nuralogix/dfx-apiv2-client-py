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
        """
        Retrieves a list of studies that act as templates or base types.

        :param session: The aiohttp ClientSession to use.
        :param status: Filter for listing by status flag.
        :return: The response from the API.
        """
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
                             limit: int = 25,
                             offset: int = 0,
                             **kwargs: Any) -> Any:
        """
        Retrieves a list of study templates that exist in a particular organization.

        :param session: The aiohttp ClientSession to use.
        :param status: Filter by template status.
        :param type_: Filter by template type.
        :param sort_order: Sort order (ASC or DESC).
        :param sort_key: Key to sort by (e.g. "Name").
        :param limit: The number of results to return.
        :param offset: The offset to start returning results from.
        :return: The response from the API.
        """
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
        """
        Creates a new study within an organization.

        :param session: The aiohttp ClientSession to use.
        :param study_name: The name of the study.
        :param description: The description of the study.
        :param study_template_id: The ID of the template to use.
        :param config: The configuration for the study.
        :return: The response from the API.
        """
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
        """
        Updates a particular study record with new information.

        :param session: The aiohttp ClientSession to use.
        :param study_id: The ID of the study to update.
        :param study_name: The new name of the study.
        :param description: The new description of the study.
        :param status: The new status of the study.
        :param config: The new configuration for the study.
        :return: The response from the API.
        """
        data = {
            "Name": study_name,
            "StatusID": status.upper(),
            "Description": description,
            "Config": config,
        }

        return await cls._patch(session, f"{cls.url_fragment}/{study_id}", data=data, **kwargs)

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, study_id: str, **kwargs: Any) -> Any:
        """
        Retrieves a study record with its definitions and values.

        :param session: The aiohttp ClientSession to use.
        :param study_id: The ID of the study to retrieve.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/{study_id}", **kwargs)

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, study_id: str, **kwargs: Any) -> Any:
        """
        Deletes a study.

        :param session: The aiohttp ClientSession to use.
        :param study_id: The ID of the study to delete.
        :return: The response from the API.
        """
        return await cls._delete(session, f"{cls.url_fragment}/{study_id}", **kwargs)

    @classmethod
    async def list(cls,
                   session: aiohttp.ClientSession,
                   date: str = "",
                   end_date: str = "",
                   study_name: str = "",
                   status: str = "",
                   limit: int = 25,
                   offset: int = 0,
                   **kwargs: Any) -> Any:
        """
        Lists all the studies created in an organization.

        :param session: The aiohttp ClientSession to use.
        :param date: Filter by study creation start date (YYYY-MM-DD).
        :param end_date: Filter by study creation end date (YYYY-MM-DD).
        :param study_name: Filter by study name.
        :param status: Filter by study status ID.
        :param limit: The number of results to return.
        :param offset: The offset to start returning results from.
        :return: The response from the API.
        """
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
        """
        Retrieves a study's binary config data that has to be used to initialize the DFX SDK Factory object.

        :param session: The aiohttp ClientSession to use.
        :param study_id: The ID of the study.
        :param sdk_id: The SDK ID.
        :param current_hash: The current MD5 hash of the config data.
        :return: The response from the API.
        """
        data = {
            "StudyID": study_id,
            "SDKID": sdk_id,
            "MD5Hash": current_hash,
        }

        return await cls._post(session, f"{cls.url_fragment}/sdkconfig", data=data, **kwargs)

    @classmethod
    async def delete_study_measurements(cls, session: aiohttp.ClientSession, study_id: str, **kwargs: Any) -> Any:
        """
        Delete measurements associated with a study.

        :param session: The aiohttp ClientSession to use.
        :param study_id: The ID of the study.
        :return: The response from the API.
        """
        warnings.warn(f"{cls.delete_study_measurements.__qualname__} is deprecated and will be removed.",
                      DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{study_id}/measurements", **kwargs)
