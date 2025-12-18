# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

import warnings
from typing import Any

import aiohttp

from .Base import Base


class Devices(Base):
    url_fragment = "devices"

    @classmethod
    async def types(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        """
        Retrieve the list of available device types.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/types", **kwargs)

    @classmethod
    async def create(cls, session: aiohttp.ClientSession, device_name: str, device_type_id: str, device_id: str,
                     version: str, **kwargs: Any) -> Any:
        """
        Create a new device.

        :param session: The aiohttp ClientSession to use.
        :param device_name: The name of the device.
        :param device_type_id: The type of the device.
        :param device_id: The unique identifier for the device (e.g. UUID).
        :param version: The version of the device.
        :return: The response from the API.
        """
        data = {
            "Name": device_name,
            "DeviceTypeID": device_type_id,
            "Identifier": device_id,  # TODO: Describe parameter
            "Version": version,
        }

        return await cls._post(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def update(cls,
                     session: aiohttp.ClientSession,
                     id: str,
                     device_name: str = "",
                     device_type_id: str = "",
                     device_id: str = "",
                     status: str = "",
                     version: str = "",
                     **kwargs: Any) -> Any:
        """
        Update an existing device.

        :param session: The aiohttp ClientSession to use.
        :param id: The ID of the device to update.
        :param device_name: The new name of the device.
        :param device_type_id: The new type of the device.
        :param device_id: The new unique identifier for the device.
        :param status: The new status of the device.
        :param version: The new version of the device.
        :return: The response from the API.
        """
        data = {
            "Name": device_name,
            "DeviceTypeID": device_type_id,
            "Status": status,
            "Identifier": device_id,  # TODO: Describe parameter
            "Version": version,
        }

        return await cls._patch(session, f"{cls.url_fragment}/{id}", data=data, **kwargs)

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, device_id: str, **kwargs: Any) -> Any:
        """
        Retrieve a device by its ID.

        :param session: The aiohttp ClientSession to use.
        :param device_id: The ID of the device to retrieve.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/{device_id}", **kwargs)

    @classmethod
    async def list(cls,
                   session: aiohttp.ClientSession,
                   status_id: str = "",
                   device_type_id: str = "",
                   device_name: str = "",
                   device_version: str = "",
                   license_id: str = "",
                   date: str = "",
                   end_date: str = "",
                   sort_order: str = "",
                   limit: int = 25,
                   offset: int = 0,
                   **kwargs: Any) -> Any:
        """
        List devices.

        :param session: The aiohttp ClientSession to use.
        :param status_id: Filter by status ID.
        :param device_type_id: Filter by device type ID.
        :param device_name: Filter by device name.
        :param device_version: Filter by device version.
        :param license_id: Filter by license ID.
        :param date: Filter by date (YYYY-MM-DD).
        :param end_date: Filter by end date (YYYY-MM-DD).
        :param sort_order: Sort order (ASC or DESC).
        :param limit: The number of results to return.
        :param offset: The offset to start returning results from.
        :return: The response from the API.
        """
        params = {
            "StatusID": status_id,
            "DeviceTypeID": device_type_id,
            "LicenseID": license_id,
            "Name": device_name,  # TODO: Verify docs
            "Version": device_version,
            "Date": date,
            "EndDate": end_date,
            "SortOrder": sort_order.upper(),
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, cls.url_fragment, params=params, **kwargs)

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, device_id: str, **kwargs: Any) -> Any:
        """
        Delete a device.

        :param session: The aiohttp ClientSession to use.
        :param device_id: The ID of the device to delete.
        :return: The response from the API.
        """
        warnings.warn(f"{cls.delete.__qualname__} is deprecated and will be removed.", DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{device_id}", **kwargs)

    @classmethod
    async def delete_measurements(cls, session: aiohttp.ClientSession, device_id: str, **kwargs: Any) -> Any:
        """
        Delete measurements associated with a device.

        :param session: The aiohttp ClientSession to use.
        :param device_id: The ID of the device.
        :return: The response from the API.
        """
        warnings.warn(f"{cls.delete_measurements.__qualname__} is deprecated and will be removed.", DeprecationWarning)

        return await cls._delete(session, f"{cls.url_fragment}/{device_id}/measurements", **kwargs)

    @classmethod
    async def retrieve_license_id(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        """
        Retrieve the license ID associated with the current device.

        :param session: The aiohttp ClientSession to use.
        :return: The response from the API.
        """
        return await cls._get(session, f"{cls.url_fragment}/license", **kwargs)
