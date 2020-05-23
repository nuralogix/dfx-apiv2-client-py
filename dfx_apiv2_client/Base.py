import aiohttp

from .Settings import Settings


class Base:
    @classmethod
    async def get(cls, session: aiohttp.ClientSession, url_fragment: str, params: dict = None):
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.get(url, params=params) as resp:
            return await resp.json()

    @classmethod
    async def post(cls, session: aiohttp.ClientSession, url_fragment: str, data: dict):
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.post(url, json=data) as resp:
            return await resp.json()

    @classmethod
    async def patch(cls, session: aiohttp.ClientSession, url_fragment: str, data: dict):
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.patch(url, json=data) as resp:
            return await resp.json()

    @classmethod
    async def delete(cls, session: aiohttp.ClientSession, url_fragment: str):
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.delete(url) as resp:
            return await resp.json()
