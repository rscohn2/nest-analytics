import json
from datetime import datetime, timezone
from os import environ
from typing import Dict, List

import pandas as pd


class Zone:
    def __init__(self, name: str) -> None:
        self.name = name
        self.status = "unknown"


def zone_map(user):
    zones = {}
    for building in user.buildings.values():
        for device in building.devices.values():
            zones[device.resource] = Zone(device.name)
    return zones


def convert_to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def retrieve_nest(user, begin: datetime, end: datetime) -> List[Dict]:
    local_file = "nest-events.json"
    replay_cmd = environ.get("HA_NEST")
    if replay_cmd == "replay":
        with open(local_file, "r") as file:
            observations = json.load(file)
    else:
        b = convert_to_iso(begin)
        e = convert_to_iso(end)
        observations = (
            user.data.collection("nest-events")
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

    zones = zone_map(user)
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
                elif trait == "sdm.devices.traits.Connectivity":
                    pass
                elif trait == "sdm.devices.traits.Humidity":
                    event["Humidity"] = value["ambientHumidityPercent"]
                elif trait == "sdm.devices.traits.ThermostatHvac":
                    if zone.status == "COOLING":
                        event["Cooling Time"] = (
                            timestamp - zone.cooling_start
                        ).seconds / 60
                    if value["status"] == "COOLING":
                        zone.cooling_start = timestamp
                    zone.status = value["status"]
                elif trait == "sdm.devices.traits.ThermostatMode":
                    pass
                elif trait == "sdm.devices.traits.ThermostatEco":
                    pass
                elif (
                    trait == "sdm.devices.traits.ThermostatTemperatureSetpoint"
                ):
                    pass
                elif trait == "sdm.devices.traits.Fan":
                    pass
                else:
                    raise ValueError(f"Unexpected trait: {trait}")
                events.append(event)
    return events
