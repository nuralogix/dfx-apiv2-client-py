# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

from typing import Any

import aiohttp

from .Base import Base


class Meta(Base):
    url_fragment = "meta"

    @classmethod
    async def retrieve(cls, session: aiohttp.ClientSession, id: str, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/{id}", **kwargs)

    @classmethod
    async def update(cls, session: aiohttp.ClientSession, id: str, data: str, **kwargs: Any) -> Any:
        return await cls._patch(session, f"{cls.url_fragment}/{id}", data=data, **kwargs)
