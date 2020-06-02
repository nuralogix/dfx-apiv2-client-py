from typing import Any, List

import aiohttp

from .Base import Base


class Groups(Base):
    url_fragment = "groups"

    @classmethod
    async def retrieve_group_types(cls, session: aiohttp.ClientSession) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/types")

    @classmethod
    async def list(cls, session: aiohttp.ClientSession, filter_type: str = "") -> Any:
        params = {
            "Type": str(filter_type),
        }

        return await cls._get(session, cls.url_fragment, params=params)

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, group_id: str) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{group_id}")

    @classmethod
    async def create(cls,
                     session: aiohttp.ClientSession,
                     group_type_id: str,
                     description: str,
                     status: str,
                     study_id: str = "") -> Any:
        data = {
            "GroupTypeID": str(group_type_id),
            "Description": str(description),
            "Status": str(status),
            "StudyID": str(study_id),
        }

        return await cls._post(session, cls.url_fragment, data=data)

    @classmethod
    async def update(cls,
                     session: aiohttp.ClientSession,
                     group_type_id: str = "",
                     description: str = "",
                     status: str = "",
                     study_id: str = "") -> Any:
        data = {
            "GroupTypeID": str(group_type_id),
            "Description": str(description),
            "Status": str(status),
            "StudyID": str(study_id),
        }

        return await cls._patch(session, cls.url_fragment, data=data)

    @classmethod
    async def remove(cls, session: aiohttp.ClientSession, group_id: str) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/{group_id}")

    @classmethod
    async def add_users(cls, session: aiohttp.ClientSession, group_id: str, user_ids: List[str]) -> Any:
        if len(user_ids) > 500:
            raise ValueError("Only 500 users can be created in one call")

        return await cls._post(session, f"{cls.url_fragment}/{group_id}/user", data=user_ids)

    @classmethod
    async def remove_users(cls, session: aiohttp.ClientSession, group_id: str, user_ids: List[str]) -> Any:
        if len(user_ids) > 500:
            raise ValueError("Only 500 users can be removed in one call")

        return await cls._delete(session, f"{cls.url_fragment}/{group_id}/user", data=user_ids)

    @classmethod
    async def list_users(cls, session: aiohttp.ClientSession, group_id: str) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{group_id}/users")
