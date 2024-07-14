import json
from datetime import datetime
from os import environ
from typing import Dict, List

import pandas as pd


def retrieve_weather(user, begin: datetime, end: datetime) -> List[Dict]:
    local_file = "weather-events.json"
    if environ.get("HA_WEATHER") == "replay":
        with open(local_file, "r") as file:
            observations = json.load(file)
    else:
        begin_timestamp = int(begin.timestamp())
        end_timestamp = int(end.timestamp())

        observations = (
            user.data.collection("weather-events")
            .where("dt", ">=", begin_timestamp)
            .where("dt", "<=", end_timestamp)
            .stream()
        )
        # sort based on dt field
        observations = sorted(
            [obs.to_dict() for obs in observations], key=lambda x: x["dt"]
        )
    if environ.get("HA_WEATHER") == "record":
        with open(local_file, "w") as file:
            json.dump(observations, file, indent=4, sort_keys=True)

    events = []
    for observation in observations:
        timestamp = (
            pd.to_datetime(observation["dt"], unit="s")
            .tz_localize("UTC")
            .tz_convert("US/Eastern")
        )
        event = {}
        event["Time"] = timestamp
        event["Zone"] = "Weather"
        event["Temperature"] = observation["main"]["temp"] * 9 / 5 + 32
        event["Humidity"] = observation["main"]["humidity"]
        events.append(event)
    print(f"Events: {events}")
    return events
