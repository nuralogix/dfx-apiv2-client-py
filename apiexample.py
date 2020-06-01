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
    creds = load_creds(args.creds_file)

    # Check API status
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        api_status = await dfxapi.General.api_status(session)
        if not api_status["StatusID"] == "ACTIVE":
            print(f"DFX API Status: {api_status['StatusID']} ({dfxapi.Settings.rest_url})")

            return

    # Register or unregister
    if args.command == "org":
        if args.subcommand == "unregister":
            success = await unregister(creds, args.creds_file)
        else:
            success = await register(creds, args.creds_file, args.license_key)

        if success:
            save_creds(creds, args.creds_file)
        return

    # Login or logout
    if args.command == "user":
        if args.subcommand == "logout":
            success = logout(creds, args.creds_file)
        else:
            success = await login(creds, args.creds_file, args.email, args.password)

        if success:
            save_creds(creds, args.creds_file)
        return

    # The commands below need a token, so make sure we are registered and/or logged in
    if not dfxapi.Settings.device_token and not dfxapi.Settings.user_token:
        print("Please register and/or login first to obtain a token")
        return

    # Use the token to create the headers
    token = dfxapi.Settings.user_token if dfxapi.Settings.user_token else dfxapi.Settings.device_token
    headers = {"Authorization": f"Bearer {token}"}

    # Retrieve or list measurements
    if args.command == "measure":
        if args.subcommand == "get":
            async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
                measurementResults = await dfxapi.Measurements.retrieve(session, args.measurement_id)
                print(f"Result: {measurementResults['StatusID']}")
                for signal, results in measurementResults["Results"].items():
                    for result in results:
                        print(f"   {signal}:{result['Data'][0]/result['Multiplier']}")
            return
        elif args.subcommand == "list":
            async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
                list_of_measurements = await dfxapi.Measurements.list(session, limit=args.limit)
                pretty_print(list_of_measurements)
            return

    # Make a measurement
    assert args.command == "measure" and args.subcommand == "make"

    # Verify preconditions
    payload_files = sorted(glob.glob(os.path.join(args.payloads_folder, "payload*.bin")))
    meta_files = sorted(glob.glob(os.path.join(args.payloads_folder, "metadata*.bin")))
    prop_files = sorted(glob.glob(os.path.join(args.payloads_folder, "properties*.json")))
    number_files = min(len(payload_files), len(meta_files), len(prop_files))
    if number_files <= 0:
        print(f"No payload files found in {args.payloads_folder}")
        return
    with open(prop_files[0], 'r') as pr:
        props = json.load(pr)
        number_chunks_pr = props["number_chunks"]
        duration_pr = props["duration_s"]
    if number_chunks_pr != number_files:
        print(f"Number of chunks in properties.json {number_chunks_pr} != Number of payload files {number_files}")
        return
    if duration_pr * number_chunks_pr > 120:
        print(f"Total payload duration {duration_pr * number_chunks_pr} seconds is more than 120 seconds")
        return

    use_websocket = not args.rest
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        # Create a measurement
        measurement_id = await dfxapi.Measurements.create(session, args.study_id)
        print(f"Created measurement {measurement_id}")

        measurement_files = zip(payload_files, meta_files, prop_files)
        # Add data to the measurement
        if use_websocket:
            # Make a measurement using WebSocket
            await measure_websocket(session, measurement_id, measurement_files)
        else:
            # Make a measurement using REST (no results are returned)
            await measure_rest(session, measurement_id, measurement_files)

        print(f"Measurement {measurement_id} complete")


def load_creds(creds_file):
    creds = {
        "device_id": "",
        "device_token": "",
        "role_id": "",
        "user_id": "",
        "user_token": "",
    }
    if os.path.isfile(creds_file):
        with open(creds_file, "r") as c:
            creds = json.loads(c.read())

    dfxapi.Settings.device_id = creds["device_id"]
    dfxapi.Settings.device_token = creds["device_token"]
    dfxapi.Settings.role_id = creds["role_id"]
    dfxapi.Settings.role_id = creds["role_id"]
    dfxapi.Settings.user_token = creds["user_token"]

    return creds


def save_creds(creds, creds_file):
    with open(creds_file, "w") as c:
        c.write(json.dumps(creds, indent=4))
        print(f"Credentials updated in {creds_file}")


def rand_reqid():
    return "".join(random.choices(string.ascii_letters, k=10))


def determine_action(chunk_number, number_chunks):
    action = 'CHUNK::PROCESS'
    if chunk_number == 0 and number_chunks > 1:
        action = 'FIRST::PROCESS'
    elif chunk_number == number_chunks - 1:
        action = 'LAST::PROCESS'
    return action


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


async def measure_rest(session, measurement_id, measurement_files):
    for payload_file, meta_file, prop_file in measurement_files:
        with open(payload_file, 'rb') as p, open(meta_file, 'rb') as m, open(prop_file, 'r') as pr:
            payload_bytes = p.read()
            meta_bytes = m.read()
            props = json.load(pr)

            # Determine action
            action = determine_action(props["chunk_number"], props["number_chunks"])

            # Add data
            chunkID = await dfxapi.Measurements.add_data(session, measurement_id, props["chunk_number"], action,
                                                         props["start_time_s"], props["end_time_s"],
                                                         props["duration_s"], meta_bytes, payload_bytes)
            print(f"Sent chunk id#:{chunkID} - {action} ...waiting {props['duration_s']:.0f} seconds...")

            # Sleep to simulate a live measurement and not hit the rate limit
            await asyncio.sleep(props["duration_s"])


async def measure_websocket(session, measurement_id, measurement_files):
    pass

def cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("--creds_file", default="./creds.json")

    subparser_top = parser.add_subparsers(dest="command", required=True)
    subparser_orgs = subparser_top.add_parser("org", help="Organizations").add_subparsers(dest="subcommand",
                                                                                          required=True)
    register_parser = subparser_orgs.add_parser("register", help="Register device")
    register_parser.add_argument("license_key", help="DFX API Organization License")
    unregister_parser = subparser_orgs.add_parser("unregister", help="Unregister device")

    subparser_users = subparser_top.add_parser("user", help="Users").add_subparsers(dest="subcommand", required=True)
    login_parser = subparser_users.add_parser("login", help="User login")
    login_parser.add_argument("email", help="Email address")
    login_parser.add_argument("password", help="Password")
    logout_parser = subparser_users.add_parser("logout", help="User logout")

    subparser_meas = subparser_top.add_parser("measure", help="Measurements").add_subparsers(dest="subcommand",
                                                                                             required=True)
    make_parser = subparser_meas.add_parser("make", help="Make a measurement")
    make_parser.add_argument("study_id", help="Study ID to use", type=str)
    make_parser.add_argument("payloads_folder", help="Folder containing payloads", type=str)
    make_parser.add_argument("--rest", help="Use REST instead of WebSocket (no results returned)", action="store_true")
    list_parser = subparser_meas.add_parser("list", help="List existing measurements")
    list_parser.add_argument("--limit", help="Number of measurements to retrieve", type=int, default=1)
    get_parser = subparser_meas.add_parser("get", help="Retrieve a measurement")
    get_parser.add_argument("measurement_id", help="ID of measurement to retrieve", type=str)

    args = parser.parse_args()

    # asyncio.run(main(args))  # https://github.com/aio-libs/aiohttp/issues/4324

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
    loop.run_until_complete(asyncio.sleep(0.25))  # https://github.com/aio-libs/aiohttp/issues/1925
    loop.close()


if __name__ == '__main__':
    cmdline()
