from .Settings import Settings


class General:
    @classmethod
    async def status(cls, session):
        url = f"{Settings.rest_url}/status"
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body

            raise ValueError((url, resp.status, body))

    @classmethod
    async def statuses(cls, session):
        url = f"{Settings.rest_url}/statuses"
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body

            raise ValueError((url, resp.status, body))

    @classmethod
    async def roles(cls, session):
        url = f"{Settings.rest_url}/roles"
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body

            raise ValueError((url, resp.status, body))

    @classmethod
    async def mimes(cls, session):
        url = f"{Settings.rest_url}/mimes"
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body

            raise ValueError((url, resp.status, body))

    @classmethod
    async def auth(cls, session):
        url = f"{Settings.rest_url}/auth"
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body

            raise ValueError((url, resp.status, body))