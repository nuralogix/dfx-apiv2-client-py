from .Settings import Settings


class Base:
    @classmethod
    async def get(cls, session, url_fragment, params=None):
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.get(url, params=params) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body

            raise ValueError((url, resp.status, body))

    @classmethod
    async def post(cls, session, url_fragment, data):
        url = f"{Settings.rest_url}/{url_fragment}"

        async with session.post(url, json=data) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body

            raise ValueError((url, resp.status, body))