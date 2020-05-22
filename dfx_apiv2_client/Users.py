from .Settings import Settings


class Users:
    url_fragment = "users"

    @classmethod
    async def retrieve(cls, session):
        url = f"{Settings.rest_url}/{cls.url_fragment}"
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body

            raise ValueError((url, resp.status, body))

    class Auth:
        url_fragment = "users/auth"

        @classmethod
        async def login(cls, session, email: str, password: str):
            data = {
                "Email": email,
                "Password": password,
            }
            url = f"{Settings.rest_url}/{cls.url_fragment}"
            async with session.post(url, json=data) as resp:
                body = await resp.json()
                if resp.status == 200:
                    Settings.user_token = body["Token"]
                    return body

                raise ValueError((url, resp.status, body))
