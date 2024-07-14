import json

import pandas as pd


def load_weather_events():
    with open("weather-events.json", "r") as file:
        observations = json.load(file)
    observations = sorted(observations, key=lambda x: x["dt"])
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


def retrieve_weather(user, begin, end):
    return load_weather_events()
