import json
from datetime import datetime, timezone
from os import environ
from typing import Dict, List

import pandas as pd
from common.data_model import db
from flask_login import current_user, login_required

from flask import Blueprint, redirect

nest_blueprint = Blueprint("nest", __name__)


class Zone:
    def __init__(self, name: str) -> None:
        self.name = name
        self.status = "unknown"


def zone_map():
    zones = {}
    for room_id, room in current_user.current_structure.rooms.items():
        for device_id, device in room["devices"].items():
            zones[device["name"]] = Zone(room["name"])
    return zones


def convert_to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def retrieve_nest(
    structure_id: str, begin: datetime, end: datetime
) -> List[Dict]:
    zones = zone_map()

    local_file = "nest-events.json"
    replay_cmd = environ.get("HA_NEST")
    if replay_cmd == "replay":
        with open(local_file, "r") as file:
            observations = json.load(file)
    else:
        b = convert_to_iso(begin)
        e = convert_to_iso(end)
        observations = (
            db.collection("nest-data")
            .where("timestamp", ">=", b)
            .where("timestamp", "<=", e)
            .stream()
        )
        # sort based on dt field
        observations = sorted(
            [obs.to_dict() for obs in observations],
            key=lambda x: x["timestamp"],
        )
    if replay_cmd == "record":
        with open(local_file, "w") as file:
            json.dump(observations, file, indent=4, sort_keys=True)

    events = []
    for observation in observations:
        timestamp = pd.to_datetime(observation["timestamp"]).tz_convert(
            "US/Eastern"
        )
        if "resourceUpdate" in observation:
            for trait, value in observation["resourceUpdate"][
                "traits"
            ].items():
                zone = zones[observation["resourceUpdate"]["name"]]
                event = {}
                event["Time"] = timestamp
                event["Zone"] = zone.name
                if trait == "sdm.devices.traits.Temperature":
                    event["Temperature"] = (
                        value["ambientTemperatureCelsius"] * 9 / 5 + 32
                    )
                elif trait == "sdm.devices.traits.Humidity":
                    event["Humidity"] = value["ambientHumidityPercent"]
                elif trait == "sdm.devices.traits.ThermostatHvac":
                    if zone.status == "COOLING":
                        event["Cooling Time"] = (
                            (timestamp - zone.cooling_start).seconds / 60 / 60
                        )
                    if value["status"] == "COOLING":
                        zone.cooling_start = timestamp
                    zone.status = value["status"]
                elif trait in (
                    "sdm.devices.traits.Connectivity",
                    "sdm.devices.traits.Fan",
                    "sdm.devices.traits.Info",
                    "sdm.devices.traits.Settings",
                    "sdm.devices.traits.ThermostatEco",
                    "sdm.devices.traits.ThermostatMode",
                    "sdm.devices.traits.ThermostatTemperatureSetpoint",
                ):
                    pass
                else:
                    raise ValueError(f"Unexpected trait: {trait}")
                events.append(event)
    return events


@nest_blueprint.route("/update", methods=["GET"])
@login_required
def update():
    current_user.link_nest()
    return redirect("/")
