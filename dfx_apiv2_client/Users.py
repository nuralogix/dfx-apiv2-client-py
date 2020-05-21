from dfx_apiv2_client import DfxApi


class Users(DfxApi):
    url_fragment = "users"

    @classmethod
    async def retrieve(cls, session):
        url = f"{DfxApi.rest_url}/{cls.url_fragment}"
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status == 200:
                return body

            raise ValueError((url, resp.status, body))

    class Auth(DfxApi):
        url_fragment = "users/auth"

        @classmethod
        async def login(cls, session, email: str, password: str):
            data = {
                "Email": email,
                "Password": password,
            }
            url = f"{DfxApi.rest_url}/{cls.url_fragment}"
            async with session.post(url, json=data) as resp:
                body = await resp.json()
                if resp.status == 200:
                    DfxApi.user_token = body["Token"]
                    return body

                raise ValueError((url, resp.status, body))
