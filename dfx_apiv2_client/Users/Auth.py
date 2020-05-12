from dfx_apiv2_client import DfxApi


class Auth(DfxApi):
    @classmethod
    async def login(cls, session, email: str, password: str):
        data = {
            "Email": email,
            "Password": password,
        }
        url_fragment = "/".join(__loader__.name.lower().split(".")[1:])
        url = f"{DfxApi.rest_url}/{url_fragment}"
        async with session.post(url, json=data) as resp:
            body = await resp.json()
            if resp.status == 200:
                DfxApi.user_token = body["Token"]
                return body

            raise ValueError((url, resp.status, body))
