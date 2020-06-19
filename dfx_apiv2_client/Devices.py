from typing import Any

import aiohttp

from .Base import Base


class Devices(Base):
    url_fragment = "devices"

    @classmethod
    async def types(cls, session: aiohttp.ClientSession) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/types")

    @classmethod
    async def create(cls, session: aiohttp.ClientSession, device_name: str, device_type_id: str, device_id: str,
                     version: str) -> Any:
        data = {
            "Name": str(device_name),
            "DeviceTypeID": str(device_type_id),
            "Identifier": str(device_id),  # TODO: What is this??
            "Version": str(version),
        }

        return await cls._post(session, cls.url_fragment, data=data)

    @classmethod
    async def update(cls, session: aiohttp.ClientSession, id: str, device_name: str, device_type_id: str,
                     device_id: str, status: str, version: str) -> Any:
        data = {
            "Name": str(device_name),
            "DeviceTypeID": str(device_type_id),
            "Status": str(status),
            "Identifier": str(device_id),  # TODO: What is this??
            "Version": str(version),
        }

        return await cls._patch(session, f"{cls.url_fragment}/{id}", data=data)

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, device_id: str) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{device_id}")

    @classmethod
    async def list(
        cls,
        session: aiohttp.ClientSession,
        status_id: str = "",
        device_type_id: str = "",
        device_name: str = "",
        device_version: str = "",
        date: str = "",
        end_date: str = "",
        limit: int = 25,
        offset: int = 0,
    ) -> Any:
        params = {
            "StatusID": status_id,
            "DeviceTypeID": device_type_id,
            "Name": device_name,
            "Date": date,
            "EndDate": end_date,
            "Limit": limit,
            "Offset": offset,
        }

        return await cls._get(session, cls.url_fragment, params=params)

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, device_id: str) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/{device_id}")
