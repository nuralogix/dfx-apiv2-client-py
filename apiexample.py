# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

import argparse
import asyncio
import glob
import json
import os.path
import platform
import random
import string

import aiohttp

import dfx_apiv2_client as dfxapi

from prettyprint import print_meas, print_pretty


async def main(args):
    # Load config
    config = load_config(args.config_file)

    # Check API status
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        _, api_status = await dfxapi.General.api_status(session)
        if not api_status["StatusID"] == "ACTIVE":
            print(f"DeepAffex Cloud API: {dfxapi.Settings.rest_url} Status: {api_status['StatusID']}")
            return

    # Register or unregister
    if args.command == "org":
        if args.subcommand == "unregister":
            success = await unregister(config)
        else:
            success = await register(config, args.license_key)

        if success:
            save_config(config, args.config_file)
        return

    # Login or logout
    if args.command == "user":
        if args.subcommand == "logout":
            success = await logout(config)
            if success:
                save_config(config, args.config_file)
            return
        elif args.subcommand == "login":
            success = await login(config, args.email, args.password)
            if success:
                save_config(config, args.config_file)
            return

    # The commands below need a token, so make sure we are registered and/or logged in
    if not dfxapi.Settings.device_token and not dfxapi.Settings.user_token:
        print("Please register and/or login first to obtain a token")
        return

    # Verify and if necessary, attempt to renew the token
    verified, renewed, headers, new_config = await verify_renew_token(config)
    if not verified:
        save_config(new_config, args.config_file)
        if not renewed:
            return

    # Create, update, remove profiles
    if args.command == "profile":
        async with aiohttp.ClientSession(headers=headers, raise_for_status=False) as session:
            if args.subcommand == "create":
                _, profile_id = await dfxapi.Profiles.create(session, args.name, args.email)
                print(json.dumps(profile_id)) if args.json else print_pretty(profile_id, args.csv)
            elif args.subcommand == "update":
                _, body = await dfxapi.Profiles.update(session, args.profile_id, args.name, args.email, args.status)
                print(json.dumps(body)) if args.json else print_pretty(body, args.csv)
            elif args.subcommand == "remove":
                _, body = await dfxapi.Profiles.delete(session, args.profile_id)
                print(json.dumps(body)) if args.json else print_pretty(body, args.csv)
            elif args.subcommand == "get":
                _, profile = await dfxapi.Profiles.retrieve(session, args.profile_id)
                print(json.dumps(profile)) if args.json else print_pretty(profile, args.csv)
            elif args.subcommand == "list":
                _, profile_list = await dfxapi.Profiles.list(session)
                print(json.dumps(profile_list)) if args.json else print_pretty(profile_list, args.csv)
        return

    # Retrieve or list studies
    if args.command == "study":
        async with aiohttp.ClientSession(headers=headers, raise_for_status=False) as session:
            if args.subcommand == "get":
                study_id = config["selected_study"] if args.study_id is None else args.study_id
                if not study_id or study_id.isspace():
                    print("Please select a study or pass a study id")
                    return
                _, study = await dfxapi.Studies.retrieve(session, study_id)
                print(json.dumps(study)) if args.json else print_pretty(study, args.csv)
            elif args.subcommand == "get_sdk_cfg_data":
                _, study_cfg = await dfxapi.Studies.retrieve_sdk_config_data(session, args.study_id, args.sdk_id,
                                                                             args.current_hash)
                print(json.dumps(study_cfg)) if args.json else print_pretty(study_cfg, args.csv)
            elif args.subcommand == "list":
                _, studies = await dfxapi.Studies.list(session)
                print(json.dumps(studies)) if args.json else print_pretty(studies, args.csv)
            elif args.subcommand == "select":
                status, response = await dfxapi.Studies.retrieve(session, args.study_id, raise_for_status=False)
                if status >= 400:
                    print_pretty(response)
                    return
                config["selected_study"] = args.study_id
                save_config(config, args.config_file)
        return

    # Retrieve or list measurements
    if args.command == "measure" and args.subcommand != "make":
        async with aiohttp.ClientSession(headers=headers, raise_for_status=False) as session:
            if args.subcommand == "get":
                measurement_id = config["last_measurement"] if args.measurement_id is None else args.measurement_id
                if not measurement_id or measurement_id.isspace():
                    print("Please complete a measurement first or pass a measurement id")
                    return
                _, results = await dfxapi.Measurements.retrieve(session, measurement_id)
                print(json.dumps(results)) if args.json else print_meas(results, args.csv)
            elif args.subcommand == "list":
                _, measurements = await dfxapi.Measurements.list(session,
                                                                 limit=args.limit,
                                                                 user_profile_id=args.profile_id,
                                                                 partner_id=args.partner_id)
                print(json.dumps(measurements)) if args.json else print_pretty(measurements, args.csv)
        return

    # Make a measurement
    assert args.command == "measure" and args.subcommand == "make"

    # Verify preconditions
    # 1. Make sure a study is selected
    if not config["selected_study"]:
        print("Please select a study first using 'study select'")
        return

    # 2. Make sure payload files exist
    payload_files = sorted(glob.glob(os.path.join(args.payloads_folder, "payload*.bin")))
    prop_files = sorted(glob.glob(os.path.join(args.payloads_folder, "properties*.json")))
    found_props = True if len(prop_files) > 0 else False
    if not found_props:
        prop_files = payload_files

    number_files = min(len(payload_files), len(prop_files))
    if number_files <= 0:
        print(f"No payload files found in {args.payloads_folder}")
        return
    if found_props:
        with open(prop_files[0], 'r') as pr:
            props = json.load(pr)
            number_chunks_pr = props["number_chunks"]
            if "duration_s" in props:
                duration_pr = props["duration_s"]
            else:
                duration_pr = props["end_time_s"] - props["start_time_s"]
                props["duration_s"] = duration_pr
        if number_chunks_pr != number_files:
            print(f"Number of chunks in properties.json {number_chunks_pr} != Number of payload files {number_files}")
            return
        if duration_pr * number_chunks_pr > 120:
            print(f"Total payload duration {duration_pr * number_chunks_pr} seconds is more than 120 seconds")
            return
    else:
        duration_pr = args.chunk_duration_s
        number_chunks_pr = number_files

    use_websocket = not args.rest
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        # Create a measurement
        _, create_result = await dfxapi.Measurements.create(session,
                                                            config["selected_study"],
                                                            user_profile_id=args.user_profile_id,
                                                            partner_id=args.partner_id)
        measurement_id = create_result["ID"]
        print(f"Created measurement {measurement_id}")

        measurement_files = zip(payload_files, prop_files)
        # Add data to the measurement
        if use_websocket:
            # Make a measurement using WebSocket
            await measure_websocket(session, measurement_id, measurement_files, number_chunks_pr, duration_pr, found_props)
        else:
            # Make a measurement using REST (no results are returned)
            await measure_rest(session, measurement_id, measurement_files, number_chunks_pr, duration_pr, found_props)

        print(f"Measurement {measurement_id} complete")

        config["last_measurement"] = measurement_id
        save_config(config, args.config_file)


def load_config(config_file):
    config = {
        "device_id": "",
        "device_token": "",
        "device_refresh_token": "",
        "role_id": "",
        "user_id": "",
        "user_token": "",
        "user_refresh_token": "",
        "selected_study": "",
        "last_measurement": "",
        "study_cfg_hash": "",
        "study_cfg_data": "",
    }
    if os.path.isfile(config_file):
        with open(config_file, "r") as c:
            read_config = json.loads(c.read())
            config = {**config, **read_config}

    dfxapi.Settings.device_id = config["device_id"]
    dfxapi.Settings.device_token = config["device_token"]
    dfxapi.Settings.device_refresh_token = config["device_refresh_token"]
    dfxapi.Settings.role_id = config["role_id"]
    dfxapi.Settings.user_id = config["user_id"]
    dfxapi.Settings.user_token = config["user_token"]
    dfxapi.Settings.user_refresh_token = config["user_refresh_token"]
    if "rest_url" in config and config["rest_url"]:
        dfxapi.Settings.rest_url = config["rest_url"]
    if "ws_url" in config and config["ws_url"]:
        dfxapi.Settings.ws_url = config["ws_url"]

    return config


def save_config(config, config_file):
    with open(config_file, "w") as c:
        c.write(json.dumps(config, indent=4))
        print(f"Credentials updated in {config_file}")


def generate_reqid():
    return "".join(random.choices(string.ascii_letters, k=10))


def determine_action(chunk_number, number_chunks):
    action = 'CHUNK::PROCESS'
    if chunk_number == 0 and number_chunks > 1:
        action = 'FIRST::PROCESS'
    elif chunk_number == number_chunks - 1:
        action = 'LAST::PROCESS'
    return action


async def register(config, license_key):
    if dfxapi.Settings.device_token:
        print("Already registered")
        return False

    try:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            await dfxapi.Organizations.register_license(session, license_key, "LINUX", "DFX Example", "DFXCLIENT",
                                                        "0.0.1")
            config["device_id"] = dfxapi.Settings.device_id
            config["device_token"] = dfxapi.Settings.device_token
            config["device_refresh_token"] = dfxapi.Settings.device_refresh_token
            config["role_id"] = dfxapi.Settings.role_id

            # The following need to be cleared since we make measurements and user/device tokens are linked
            config["user_token"] = dfxapi.Settings.user_token = ""
            config["user_refresh_token"] = dfxapi.Settings.user_refresh_token = ""

            print(f"Register successful with new device id {config['device_id']}")
        return True
    except aiohttp.ClientResponseError as e:
        print(f"Register failed: {e}")
        return False


async def unregister(config):
    if not dfxapi.Settings.device_token:
        print("Not registered")
        return False

    headers = {"Authorization": f"Bearer {dfxapi.Settings.device_token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        status, body = await dfxapi.Organizations.unregister_license(session)
        if status < 400:
            print(f"Unregister successful for device id {config['device_id']}")
            config["device_id"] = ""
            config["device_token"] = ""
            config["device_refresh_token"] = ""
            config["role_id"] = ""

            # The following need to be cleared since we make measurements and user/device tokens are linked
            config["user_token"] = dfxapi.Settings.user_token = ""
            config["user_refresh_token"] = dfxapi.Settings.user_refresh_token = ""

            return True
        else:
            print(f"Unregister failed {status}: {body}")


async def login(config, email, password):
    if dfxapi.Settings.user_token:
        print("Already logged in")
        return False

    if not dfxapi.Settings.device_token:
        print("Please register first to obtain a device_token")
        return False

    headers = {"Authorization": f"Bearer {dfxapi.Settings.device_token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        status, body = await dfxapi.Users.login(session, email, password)
        if status < 400:
            config["user_token"] = dfxapi.Settings.user_token
            config["user_refresh_token"] = dfxapi.Settings.user_refresh_token

            print("Login successful")
            return True
        else:
            print(f"Login failed {status}: {body}")
            return False


async def logout(config):
    if not dfxapi.Settings.user_token:
        print("Not logged in")
        return False

    headers = {"Authorization": f"Bearer {dfxapi.Settings.user_token}"}
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        await dfxapi.Users.logout(session)
        config["user_token"] = dfxapi.Settings.user_token
        config["user_refresh_token"] = dfxapi.Settings.user_refresh_token
        config["user_id"] = ""

        print("Logout successful")
    return True


async def verify_renew_token(config):
    # Use the token to create the headers
    if dfxapi.Settings.user_token:
        headers = {"Authorization": f"Bearer {dfxapi.Settings.user_token}"}
        using_user_token = True
    else:
        headers = {"Authorization": f"Bearer {dfxapi.Settings.device_token}"}
        using_user_token = False

    # Verify that our token is still valid and renew if it's not
    async with aiohttp.ClientSession(headers=headers, raise_for_status=False) as session:
        status, body = await dfxapi.General.verify_token(session)
        if status < 400:
            return True, False, headers, None

        # It's not valid, so attempt to renew it...
        if using_user_token:
            renew_status, renew_body = await dfxapi.Auths.renew_user_token(session)
        else:
            renew_status, renew_body = await dfxapi.Auths.renew_device_token(session)

        # Renew failed
        if renew_status >= 400:
            # Show error from verify_token failure
            print(f"Your {'user' if using_user_token else 'device'} token could not be verified.")
            print_pretty(body)

            # Show error from renew_token failure
            print("Attempted token refresh but failed, please register and/or login again!")
            print_pretty(renew_body)

            # Erase saved tokens
            if using_user_token:
                config["user_token"] = ""
                config["user_refresh_token"] = ""
            else:
                config["device_id"] = ""
                config["device_token"] = ""
                config["device_refresh_token"] = ""
                config["role_id"] = ""
                config["user_id"] = ""

            # Exit since we cannot continue
            return False, False, None, config

        # Renew worked, so save new tokens
        if using_user_token:
            config["user_token"] = dfxapi.Settings.user_token
            config["user_refresh_token"] = dfxapi.Settings.user_refresh_token

            # Adjust headers
            headers = {"Authorization": f"Bearer {dfxapi.Settings.user_token}"}
        else:
            config["device_token"] = dfxapi.Settings.device_token
            config["device_refresh_token"] = dfxapi.Settings.device_refresh_token

            # Adjust headers
            headers = {"Authorization": f"Bearer {dfxapi.Settings.device_token}"}

        # Continue
        print("Refreshed token. Continuing with command...")

        return False, True, headers, config


async def measure_rest(session, measurement_id, measurement_files, number_chunks, duration_args, found_prop_files):
    results_expected = number_chunks

    async def send_chunks():
        for i, (payload_file, prop_file) in enumerate(measurement_files):
            with open(payload_file, 'rb') as p, open(prop_file, 'r') as pr:
                payload_bytes = p.read()

                duration = duration_args
                if found_prop_files:
                    props = json.load(pr)
                    if "duration_s" not in props:
                        props["duration_s"] = props["end_time_s"] - props["start_time_s"]
                    duration = props["duration_s"]
                    number_chunks = props["number_chunks"]
                    chunk_number = props["chunk_number"]
                else:
                    chunk_number = i

                # Determine action
                action = determine_action(chunk_number, number_chunks)

                # Add data
                status, add_data_res = await dfxapi.Measurements.add_data(session, measurement_id, action, payload_bytes)
                chunkID = add_data_res["ID"]
                print(f"Sent chunk id#:{chunkID} - {action} ...waiting {duration:.0f} seconds...")

                # Sleep to simulate a live measurement and not hit the rate limit
                await asyncio.sleep(duration)

    async def receive_results():
        # Coroutine to receive results
        num_results_received = 0

        # receive results via polling REST every 5 seconds
        while num_results_received < results_expected:
            # Sleep to simulate a live measurement and not hit the rate limit
            await asyncio.sleep(5)

            status, response = await dfxapi.Measurements.retrieve_intermediate(session, measurement_id, num_results_received)
            if response != {}:
                print(f" Received and decoded result: {response}")
                num_results_received += 1
            else:
                print("Too early", response)

    # Start the two coroutines and await till they finish
    await asyncio.gather(send_chunks(), receive_results())


async def measure_websocket(session: aiohttp.ClientSession, measurement_id, measurement_files, number_chunks,
                            duration_args, found_prop_files):
    # Use the session to connect to the WebSocket
    async with dfxapi.Measurements.ws_connect(session) as ws:
        # Auth using `ws_auth_with_token` if headers cannot be manipulated
        if "Authorization" not in session.headers:
            await dfxapi.Organizations.ws_auth_with_token(ws, generate_reqid())
            await ws.receive()  # Wait to receive response before proceeding..

        # Subscribe to results
        results_request_id = generate_reqid()
        await dfxapi.Measurements.ws_subscribe_to_results(ws, generate_reqid(), measurement_id, results_request_id)

        # Use this to close WebSocket in the receive loop
        results_expected = number_chunks

        async def send_chunks():
            number_chunks = results_expected
            # Coroutine to iterate through the payload files and send chunks using WebSocket
            for i, (payload_file, prop_file) in enumerate(measurement_files):
                with open(payload_file, 'rb') as p, open(prop_file, 'r') as pr:
                    payload_bytes = p.read()

                    duration = duration_args
                    if found_prop_files:
                        props = json.load(pr)
                        if "duration_s" not in props:
                            props["duration_s"] = props["end_time_s"] - props["start_time_s"]
                        duration = props["duration_s"]
                        number_chunks = props["number_chunks"]
                        chunk_number = props["chunk_number"]
                    else:
                        chunk_number = i

                    # Determine action and request id
                    action = determine_action(chunk_number, number_chunks)
                    request_id = generate_reqid()

                    # Add data
                    await dfxapi.Measurements.ws_add_data(ws, request_id, measurement_id, action, payload_bytes)
                    sleep_time = max(duration, duration_args)
                    print(f"Sent chunk req#:{request_id} - {action} ...waiting {sleep_time:.0f} seconds...")

                    # Sleep to simulate a live measurement and not hit the rate limit
                    await asyncio.sleep(sleep_time)

        async def receive_results():
            # Coroutine to receive results
            num_results_received = 0
            async for msg in ws:
                _, request_id, payload = dfxapi.Measurements.ws_decode(msg)
                if request_id == results_request_id:
                    response = json.loads(payload)
                    print(f" Received and decoded result: {response}")
                    num_results_received += 1
                if num_results_received == results_expected:
                    await ws.close()
                    break

        # Start the two coroutines and await till they finish
        await asyncio.gather(send_chunks(), receive_results())


def cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config_file", default="./config.json")
    pp_group = parser.add_mutually_exclusive_group()
    pp_group.add_argument("--json", help="Print as JSON", action="store_true", default=False)
    pp_group.add_argument("--csv", help="Print grids as CSV", action="store_true", default=False)

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

    subparser_profiles = subparser_top.add_parser("profile", help="profiles").add_subparsers(dest="subcommand",
                                                                                             required=True)
    profile_create_parser = subparser_profiles.add_parser("create", help="Create profile")
    profile_create_parser.add_argument("name", help="Name (must be unique)", type=str)
    profile_create_parser.add_argument("--email", help="Email", type=str, default="no_email_provided")
    profile_update_parser = subparser_profiles.add_parser("update", help="Update a profile")
    profile_update_parser.add_argument("profile_id", help="Profile ID to update", type=str)
    profile_update_parser.add_argument("name", help="New Name", type=str, default="")
    profile_update_parser.add_argument("email", help="New Email", type=str, default="")
    profile_update_parser.add_argument("status", help="New Status", type=str, default="")
    profile_remove_parser = subparser_profiles.add_parser("remove", help="Remove a profile")
    profile_remove_parser.add_argument("profile_id", help="Profile ID to remove", type=str)
    profile_get_parser = subparser_profiles.add_parser("get", help="Retrieve a profile")
    profile_get_parser.add_argument("profile_id", help="Profile ID to retrieve", type=str)
    profile_list_parser = subparser_profiles.add_parser("list", help="List profiles")

    subparser_studies = subparser_top.add_parser("study", help="Studies").add_subparsers(dest="subcommand",
                                                                                         required=True)
    study_list_parser = subparser_studies.add_parser("list", help="List existing studies")
    study_get_parser = subparser_studies.add_parser("get", help="Retrieve a study")
    study_get_parser.add_argument("study_id",
                                  nargs="?",
                                  help="ID of study to retrieve (default: selected study)",
                                  type=str)
    study_select_parser = subparser_studies.add_parser("select", help="Select a study to use")
    study_select_parser.add_argument("study_id", help="ID of study to use", type=str)
    study_file_parser = subparser_studies.add_parser("get_sdk_cfg_data",
                                                     help="Retrieve a study config file to use with DFX SDK")
    study_file_parser.add_argument("sdk_id", help="DFX SDK ID", type=str)
    study_file_parser.add_argument("current_hash", help="Current hash value", type=str)

    subparser_meas = subparser_top.add_parser("measure", help="Measurements").add_subparsers(dest="subcommand",
                                                                                             required=True)
    make_parser = subparser_meas.add_parser("make", help="Make a measurement")
    make_parser.add_argument("payloads_folder", help="Folder containing payloads", type=str)
    make_parser.add_argument("--rest", help="Use REST instead of WebSocket (no results returned)", action="store_true")
    make_parser.add_argument("--user_profile_id", help="Set the Profile ID (Participant ID)", type=str, default="")
    make_parser.add_argument("--partner_id", help="Set the PartnerID", type=str, default="")
    make_parser.add_argument("--chunk_duration_s",
                             help="Chunk duration to use when no property files in payloads folder",
                             default=5.0)
    list_parser = subparser_meas.add_parser("list", help="List existing measurements")
    list_parser.add_argument("--limit", help="Number of measurements to retrieve (default 1)", type=int, default=1)
    list_parser.add_argument("--profile_id", help="Filter list by Profile ID", type=str, default="")
    list_parser.add_argument("--partner_id", help="Filter list by PartnerID", type=str, default="")
    get_parser = subparser_meas.add_parser("get", help="Retrieve a measurement")
    get_parser.add_argument("measurement_id",
                            nargs="?",
                            help="ID of measurement to retrieve (default: last measurement)",
                            default=None)

    args = parser.parse_args()

    # https://github.com/aio-libs/aiohttp/issues/4324
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(args))


if __name__ == '__main__':
    cmdline()
