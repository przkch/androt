#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pandas",
#     "pyyaml",
#     "requests",
# ]
# ///

import json
import yaml
import os
import pandas as pd
import requests


def getPlayDevices():
    url = "http://storage.googleapis.com/play_public/supported_devices.csv"

    df = pd.read_csv(url, encoding="utf-16")

    devices = []

    for line in df.itertuples():
        retail_branding = str(line[1])
        marketing_name = str(line[2])
        device = str(line[3])
        model = str(line[4])

        if marketing_name.lower().startswith(retail_branding.lower()):
            name = f"{marketing_name} ({model})"
        elif marketing_name.lower() == retail_branding.lower():
            name = f"{retail_branding} {model}"
        else:
            name = f"{retail_branding} {marketing_name} ({model})"

        devices.append(
            {
                "codename": device,
                "retail_branding": retail_branding,
                "marketing_name": marketing_name,
                "model": model,
                "name": name,
            }
        )

    with open("dist/play_devices.json", "w") as f:
        f.write(json.dumps(devices, indent=2))
    with open("dist/play_devices.min.json", "w") as f:
        f.write(json.dumps(devices))

    return devices


def getLocalDevices():
    with open("local.yml") as f:
        data = yaml.load(f.read(), Loader=yaml.CLoader)

    devices = []

    for oem in data:
        for codename in data[oem]:
            model = data[oem][codename]

            devices.append(
                {
                    "codename": codename,
                    "retail_branding": oem,
                    "marketing_name": model,
                    "model": "nan",
                    "name": f"{oem} {model}",
                }
            )

    return devices


def getLineageDevices():
    url = "https://download.lineageos.org/api/v2/oems"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    devices = []

    for oem in data:
        oem_name = oem["name"]
        for device in oem["devices"]:
            devices.append(
                {
                    "codename": device["model"],
                    "retail_branding": oem_name,
                    "marketing_name": device["name"],
                    "model": "nan",
                    "name": (
                        device["name"]
                        if device["name"].startswith(oem_name)
                        else f"{oem_name} {device['name']}"
                    ),
                }
            )

    return devices


def getMobileModels():
    oems = [
        "apple_all_en",
        "blackshark_en",
        "google",
        "honor_global_en",
        "huawei_global_en",
        "meizu_en",
        "mitv_global_en",
        "motorola",
        "nothing",
        "oneplus_en",
        "oppo_global_en",
        "realme_global_en",
        "vivo_global_en",
        "xiaomi_en",
    ]

    devices = []
    for oem in oems:
        oem_name = oem.replace("_en", "").replace("_global", "").replace("_all", "")

        url = f"https://raw.githubusercontent.com/KHwang9883/MobileModels/refs/heads/master/brands/{oem}.md"
        response = requests.get(url)
        data = response.text

        name = None
        model = None
        codename = None

        for line in data.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("**"):
                line = line.replace("**", "").replace(":", "").strip()

                if all([m in line for m in ["(", ")", "`"]]):
                    name = line.split("/")[0].split("(`")[0].strip()
                    try:
                        codename = line.split("(`")[1].replace("`)", "")
                    except Exception:
                        print(f"Failed processing line: '{line}'")

                else:
                    name = line
                    codename = "nan"

                continue

            if line.startswith("`"):
                model, name = line.replace("`", "", 1).split("`: ")

                devices.append(
                    {
                        "codename": codename,
                        "retail_branding": oem_name,
                        "marketing_name": name,
                        "model": model,
                        "name": (
                            name
                            if name.lower().startswith(oem_name.lower())
                            else f"{oem_name} {name}"
                        ),
                    }
                )

    return devices


def main():
    if not os.path.exists("dist/"):
        os.makedirs("dist/")

    # TODO: Sort this list
    devices = (
        *getPlayDevices(),
        *getLocalDevices(),
        *getLineageDevices(),
        *getMobileModels(),
    )

    with open("dist/devices.json", "w") as f:
        f.write(json.dumps(devices, indent=2))
    with open("dist/devices.min.json", "w") as f:
        f.write(json.dumps(devices))


if __name__ == "__main__":
    main()
