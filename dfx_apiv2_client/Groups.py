from typing import Any, List

import aiohttp

from .Base import Base


class Groups(Base):
    url_fragment = "groups"

    @classmethod
    async def retrieve_group_types(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/types", **kwargs)

    @classmethod
    async def list(cls, session: aiohttp.ClientSession, filter_type: str = "", **kwargs: Any) -> Any:
        params = {
            "Type": str(filter_type),
        }

        return await cls._get(session, cls.url_fragment, params=params, **kwargs)

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, group_id: str, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{group_id}", **kwargs)

    @classmethod
    async def create(cls,
                     session: aiohttp.ClientSession,
                     group_type_id: str,
                     description: str,
                     status: str,
                     study_id: str = "",
                     **kwargs: Any) -> Any:
        data = {
            "GroupTypeID": str(group_type_id),
            "Description": str(description),
            "Status": str(status),
            "StudyID": str(study_id),
        }

        return await cls._post(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def update(cls,
                     session: aiohttp.ClientSession,
                     group_type_id: str = "",
                     description: str = "",
                     status: str = "",
                     study_id: str = "",
                     **kwargs: Any) -> Any:
        data = {
            "GroupTypeID": str(group_type_id),
            "Description": str(description),
            "Status": str(status),
            "StudyID": str(study_id),
        }

        return await cls._patch(session, cls.url_fragment, data=data, **kwargs)

    @classmethod
    async def remove(cls, session: aiohttp.ClientSession, group_id: str, **kwargs: Any) -> Any:
        return await cls._delete(session, f"{cls.url_fragment}/{group_id}", **kwargs)

    @classmethod
    async def add_users(cls, session: aiohttp.ClientSession, group_id: str, user_ids: List[str], **kwargs: Any) -> Any:
        if len(user_ids) > 500:
            raise ValueError("Only 500 users can be created in one call")

        return await cls._post(session, f"{cls.url_fragment}/{group_id}/user", data=user_ids, **kwargs)

    @classmethod
    async def remove_users(cls, session: aiohttp.ClientSession, group_id: str, user_ids: List[str],
                           **kwargs: Any) -> Any:
        if len(user_ids) > 500:
            raise ValueError("Only 500 users can be removed in one call")

        return await cls._delete(session, f"{cls.url_fragment}/{group_id}/user", data=user_ids, **kwargs)

    @classmethod
    async def list_users(cls, session: aiohttp.ClientSession, group_id: str, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{group_id}/users", **kwargs)
