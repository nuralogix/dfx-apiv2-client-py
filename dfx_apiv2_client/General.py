from typing import Any

import aiohttp

from .Base import Base


class General(Base):
    @classmethod
    async def api_status(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._get(session, "status", **kwargs)

    @classmethod
    async def list_available_statuses(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._get(session, "statuses", **kwargs)

    @classmethod
    async def list_available_user_roles(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._get(session, "roles", **kwargs)

    @classmethod
    async def list_accepted_mime_types(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._get(session, "mimes", **kwargs)

    @classmethod
    async def verify_token(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._get(session, "auth", **kwargs)
