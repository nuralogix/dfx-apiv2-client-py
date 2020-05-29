import argparse
import asyncio
import glob
import json
import os.path
import random
import string

import aiohttp

import dfx_apiv2_client as dfxapi


async def main(args):
    # dfxapi.Settings.rest_url = "https://api2.api.deepaffex.ai:9443"

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

    dfxapi.Settings.device_id = creds["device_id"]
    dfxapi.Settings.device_token = creds["device_token"]
    dfxapi.Settings.role_id = creds["role_id"]
    dfxapi.Settings.role_id = creds["role_id"]
    dfxapi.Settings.user_token = creds["user_token"]

    # Check API status
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        api_status = await dfxapi.General.api_status(session)
        if not api_status["StatusID"] == "ACTIVE":
            print(f"DFX API Status: {api_status['StatusID']} ({dfxapi.Settings.rest_url})")

            return

    # Register or unregister
    if args.command == "register":
        if args.unregister:
            success = await unregister(creds, args.creds_file)
        else:
            success = await register(creds, args.creds_file, args.license_key)

        if success:
            update_creds_file(creds, args.creds_file)
        return

    # Login or logout
    if args.command == "login":
        if args.logout:
            success = logout(creds, args.creds_file)
        else:
            success = await login(creds, args.creds_file, args.email, args.password)

        if success:
            update_creds_file(creds, args.creds_file)
        return

    # Make sure we are registered and/or logged in
    if not dfxapi.Settings.device_token and not dfxapi.Settings.user_token:
        print("Please register and/or login first to obtain a token")
        return

    # Use the token to create the headers
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}

    # Retrieve or list measurements
    if args.command == "measurements":
        if args.retrieve is None and args.list is None:
            return
        async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
            if args.retrieve is not None:  # Retrieve
                measurementResults = await dfxapi.Measurements.retrieve(session, args.retrieve)
                print(f"Result: {measurementResults['StatusID']}")
                for signal, results in measurementResults["Results"].items():
                    for result in results:
                        print(f"   {signal}:{result['Data'][0]/result['Multiplier']}")
            else:  # or List
                list_of_measurements = await dfxapi.Measurements.list(session, limit=args.list)
                pretty_print(list_of_measurements)

            return

    # Do a measurement
    # Read the files
    payload_files = sorted(glob.glob(os.path.join(args.payloads_folder, "payload*.bin")))
    meta_files = sorted(glob.glob(os.path.join(args.payloads_folder, "metadata*.bin")))
    prop_files = sorted(glob.glob(os.path.join(args.payloads_folder, "properties*.json")))
    number_chunks = min(len(payload_files), len(meta_files), len(prop_files))

    if number_chunks <= 0:
        print(f"No payload files found in {args.payloads_folder}")
        return

    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        # Create a measurement
        measurementID = await dfxapi.Measurements.create(session, args.study_id)
        print(f"Created measurement {measurementID}")

        # Iterate through the payload files and send chunks
        for payload_file, meta_file, prop_file in zip(payload_files, meta_files, prop_files):
            with open(payload_file, 'rb') as p, open(meta_file, 'rb') as m, open(prop_file, 'r') as pr:
                payload_bytes = p.read()
                meta_bytes = m.read()
                props = json.load(pr)

                # Determine action
                action = 'CHUNK::PROCESS'
                if props["chunk_number"] == 0 and props["number_chunks"] > 1:
                    action = 'FIRST::PROCESS'
                elif props["chunk_number"] == props["number_chunks"] - 1:
                    action = 'LAST::PROCESS'

                chunkID = await dfxapi.Measurements.add_data(session, measurementID, props["chunk_number"], action,
                                                             props["start_time_s"], props["end_time_s"], meta_bytes,
                                                             payload_bytes)
                print(f"Sent chunk #{chunkID} ({action}) ...waiting {props['duration_s']:.0f} seconds...")
                # Sleep to simulate a live measurement and not hit the rate limit
                await asyncio.sleep(props["duration_s"])

        # Retrieve results
        print("Measurement complete")


def update_creds_file(creds, creds_file):
    with open(creds_file, "w") as c:
        c.write(json.dumps(creds, indent=4))
        print(f"Credentials updated in {creds_file}")


def rand_reqid():
    return "".join(random.choices(string.ascii_letters, k=10))


def pretty_print(list_of_dicts):
    if len(list_of_dicts) <= 0:
        return
    col_widths = [max(len(str(k)), len(str(v))) for (k, v) in list_of_dicts[0].items()]
    print("".join([f"{str(key):{cw}} " for (cw, key) in zip(col_widths, list_of_dicts[0].keys())]))
    for m in list_of_dicts:
        print("".join([f"{str(value):{cw}} " for (cw, value) in zip(col_widths, m.values())]))


async def register(creds, creds_file, license_key):
    if dfxapi.Settings.device_token:
        print("Already registered")
        return False

    # TODO: Handle 404 properly here...
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        await dfxapi.Organizations.register_license(session, license_key, "LINUX", "DFX Example", "DFXCLIENT", "0.0.1")
        creds["device_id"] = dfxapi.Settings.device_id
        creds["device_token"] = dfxapi.Settings.device_token
        creds["role_id"] = dfxapi.Settings.role_id
        creds["user_token"] = dfxapi.Settings.user_token
        print(f"Register successful with new device id {creds['device_id']}")
    return True


async def unregister(creds, creds_file):
    if not dfxapi.Settings.device_token:
        print("Not registered")
        return False

    headers = {"Authorization": f"Bearer {dfxapi.Settings.device_token}"}
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        await dfxapi.Organizations.unregister_license(session)
        print(f"Unregister successful for device id {creds['device_id']}")
        creds["device_id"] = ""
        creds["device_token"] = ""
        creds["role_id"] = ""
    return True


async def login(creds, creds_file, email, password):
    if dfxapi.Settings.user_token:
        print("Already logged in")
        return False

    if not dfxapi.Settings.device_token:
        print("Please register first to obtain a device_token")
        return False

    headers = {"Authorization": f"Bearer {dfxapi.Settings.device_token}"}
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        await dfxapi.Users.login(session, email, password)
        creds["user_token"] = dfxapi.Settings.user_token
        print("Login successful")
    return True


def logout(creds, creds_file):
    creds["user_token"] = ""
    creds["user_id"] = ""
    print("Logout successful")
    return True


def cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("--creds_file", default="./creds.json")

    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_reg = subparsers.add_parser("register")
    parser_reg.add_argument("license_key", help="DFX API Organization License")
    parser_reg.add_argument("--unregister", help="Unregister (license_key will be ignored)", action="store_true")

    parser_login = subparsers.add_parser("login")
    parser_login.add_argument("email", help="Email address")
    parser_login.add_argument("password", help="Password")
    parser_login.add_argument("--logout", help="Logout (email and password will be ignored)", action="store_true")

    parser_measure = subparsers.add_parser("measure")
    parser_measure.add_argument("study_id")
    parser_measure.add_argument("payloads_folder")

    parser_measurements = subparsers.add_parser("measurements")
    group_measurements = parser_measurements.add_mutually_exclusive_group()
    group_measurements.add_argument("--list", metavar="N", help="List the last N measurements made", type=int)
    group_measurements.add_argument("--retrieve", metavar="ID", help="Retrieve a measurements by ID", type=str)

    args = parser.parse_args()

    # asyncio.run(main(args))  # https://github.com/aio-libs/aiohttp/issues/4324

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
    loop.run_until_complete(asyncio.sleep(0.25))  # https://github.com/aio-libs/aiohttp/issues/1925
    loop.close()


if __name__ == '__main__':
    cmdline()
