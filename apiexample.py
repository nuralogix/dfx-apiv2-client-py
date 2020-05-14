import argparse
import asyncio
import glob
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

    # Measure
    if not dfxapi.DfxApi.device_token and not dfxapi.DfxApi.user_token:
        print("Please register and/or login first to obtain a token")
        return

    # Read the files
    payload_files = sorted(glob.glob(os.path.join(args.payloads_folder, "payload*.bin")))
    meta_files = sorted(glob.glob(os.path.join(args.payloads_folder, "metadata*.bin")))
    prop_files = sorted(glob.glob(os.path.join(args.payloads_folder, "properties*.json")))
    number_chunks = min(len(payload_files), len(meta_files), len(prop_files))

    if number_chunks <= 0:
        print(f"No payload files found in {args.payloads_folder}")
        return

    token = dfxapi.DfxApi.user_token if dfxapi.DfxApi.user_token else dfxapi.DfxApi.device_token
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
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
        await asyncio.sleep(5)
        measurementResults = await dfxapi.Measurements.retrieve(session, measurementID)
        print(f"Result: {measurementResults['StatusID']}")
        for signal, results in measurementResults["Results"].items():
            for result in results:
                print(f"   {signal}:{result['Data'][0]/result['Multiplier']}")


def cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("--creds_file", default="./creds.json")

    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_reg = subparsers.add_parser("register")
    parser_reg.add_argument("license_key")

    parser_login = subparsers.add_parser("login")
    parser_login.add_argument("email")
    parser_login.add_argument("password")

    parser_measure = subparsers.add_parser("measure")
    parser_measure.add_argument("study_id")
    parser_measure.add_argument("payloads_folder")

    args = parser.parse_args()

    # asyncio.run(main(args))  # https://github.com/aio-libs/aiohttp/issues/4324

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
    loop.run_until_complete(asyncio.sleep(0.25))  # https://github.com/aio-libs/aiohttp/issues/1925
    loop.close()


if __name__ == '__main__':
    cmdline()
