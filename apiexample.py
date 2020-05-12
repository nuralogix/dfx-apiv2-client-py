import argparse
import asyncio
import json
import os.path

import aiohttp

import dfx_apiv2_client as dfxapi


async def main(args):
    # dfxapi.DfxApi.rest_url = "https://api2.api.deepaffex.ai:9443"

    # Load creds
    creds = {
        "device_id": "",
        "device_token": "",
        "role_id": "",
        "user_id": "",
        "user_token": "",
    }
    if os.path.isfile(args.creds_file):
        with open(args.creds_file, "r") as c:
            creds = json.loads(c.read())

    dfxapi.DfxApi.device_id = creds["device_id"]
    dfxapi.DfxApi.device_token = creds["device_token"]
    dfxapi.DfxApi.role_id = creds["role_id"]
    dfxapi.DfxApi.role_id = creds["role_id"]
    dfxapi.DfxApi.user_token = creds["user_token"]

    # Register if we haven't
    if args.command == "register":
        if not dfxapi.DfxApi.device_token:
            async with aiohttp.ClientSession() as session:
                await dfxapi.Organizations.Licenses.register(session, args.license_key, "LINUX", "DFX Example",
                                                             "DFXCLIENT", "0.0.1")
                creds["device_id"] = dfxapi.DfxApi.device_id
                creds["device_token"] = dfxapi.DfxApi.device_token
                creds["role_id"] = dfxapi.DfxApi.role_id
                creds["user_token"] = dfxapi.DfxApi.user_token
                print("Register successful")

                with open(args.creds_file, "w") as c:
                    c.write(json.dumps(creds, indent=4))
        else:
            print("Already registered")

        return

    # Login if we haven't
    if args.command == "login":
        if not dfxapi.DfxApi.device_token:
            print("Please register first to obtain a device_token")
            return

        if not dfxapi.DfxApi.user_token:
            headers = {"Authorization": f"Bearer {dfxapi.DfxApi.device_token}"}
            async with aiohttp.ClientSession(headers=headers) as session:
                await dfxapi.Users.Auth.login(session, args.email, args.password)
                creds["user_token"] = dfxapi.DfxApi.user_token
                print("Login successful")

                with open(args.creds_file, "w") as c:
                    c.write(json.dumps(creds, indent=4))
        else:
            print("Already logged in")

        return


def cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("--creds_file", default="./creds.json")

    subparsers = parser.add_subparsers(dest="command")
    parser_reg = subparsers.add_parser("register")
    parser_reg.add_argument("license_key")

    parser_login = subparsers.add_parser("login")
    parser_login.add_argument("email")
    parser_login.add_argument("password")

    args = parser.parse_args()

    # asyncio.run(main(args))  # https://github.com/aio-libs/aiohttp/issues/4324

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
    loop.run_until_complete(asyncio.sleep(0.25))  # https://github.com/aio-libs/aiohttp/issues/1925
    loop.close()


if __name__ == '__main__':
    cmdline()
