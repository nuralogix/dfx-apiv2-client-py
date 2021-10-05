# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

from typing import Any

import aiohttp

from .Base import Base


class Licenses(Base):
    url_fragment = "licenses"

    @classmethod
    async def list(cls, session: aiohttp.ClientSession, **kwargs: Any) -> Any:
        return await cls._get(session, f"{cls.url_fragment}/organization", **kwargs)
