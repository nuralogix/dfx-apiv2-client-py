from typing import Any

import aiohttp

from .Base import Base


class Studies(Base):
    url_fragment = "studies"

    @classmethod
    async def types(cls, session: aiohttp.ClientSession, status: str) -> Any:
        params = {}
        if status:
            params["Status"] = status
        return await cls._get(session, f"{cls.url_fragment}/types", params=params)

    @classmethod
    async def list_templates(cls, session: aiohttp.ClientSession, status: str, type_: str) -> Any:
        params = {}
        if status:
            params["Status"] = status
        if type_:
            params["Type"] = type_
        return await cls._get(session, f"{cls.url_fragment}/templates   ", params=params)

    @classmethod
    async def create(cls, session: aiohttp.ClientSession, study_name: str, description: str, study_template_id: str,
                     config: dict) -> Any:
        data = {
            "Name": str(study_name),
            "Description": str(description),
            "StudyTemplateID": study_template_id,
            "Config": config,
        }

        return await cls._post(session, cls.url_fragment, data=data)

    @classmethod
    async def update(cls, session: aiohttp.ClientSession, study_id: str, study_name: str, description: str,
                     config: dict) -> Any:
        data = {
            "Name": str(study_name),
            "Description": str(description),
            "Config": config,
        }

        return await cls._patch(session, f"{cls.url_fragment}/{study_id}", data=data)

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, study_id: str) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{study_id}")

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, study_id: str) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/{study_id}")

    @classmethod
    async def list(cls, session: aiohttp.ClientSession, status: str = "") -> Any:
        params = {}
        if status:
            params["Status"] = status

        return await cls._get(session, cls.url_fragment, params=params)
