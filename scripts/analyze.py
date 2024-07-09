import json

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

matplotlib.rcParams["timezone"] = "US/Eastern"

zones = {
    "enterprises/a7fa74ba-12cd-4339-9d78-69ec04966021/devices/AVPHwEuLJsbdBjWkMFyPB6SKwfXsqSiDObYXgJJyy6jrTlHkEqnn2xWzH3JStzDJ2fLv7m__tKAsdjLqxyoE9ptFowYxXg": {  # noqa
        "name": "Master Bedroom",
        "status": "Off",
    },
    "enterprises/a7fa74ba-12cd-4339-9d78-69ec04966021/devices/AVPHwEuZudsIhRFpxmh9v-OQB0AB6fOUpZR0HLLsPjuvvPHiyTqalvorxtMktaunEWS03UEey0UmlFFg99IjjYwyvo88fQ": {  # noqa
        "name": "1st Floor",
        "status": "Off",
    },
    "enterprises/a7fa74ba-12cd-4339-9d78-69ec04966021/devices/AVPHwEvVxjkpbUPFJIQ4woOybkxMgp4_4HrURh2aBdksiLKRBJwwaqPIJ6tacRc4ftGfYJPckgo8wni_rl06pG460hOdvw": {  # noqa
        "name": "2nd Floor",
        "status": "Off",
    },
}


def load_nest_events():
    with open("nest-events.json", "r") as file:
        messages = json.load(file)
    events = []
    for message in messages:
        if "resourceUpdate" in message:
            timestamp = pd.to_datetime(message["timestamp"]).tz_convert(
                "US/Eastern"
            )
            zone = zones[message["resourceUpdate"]["name"]]
            for trait, value in message["resourceUpdate"]["traits"].items():
                event = {}
                event["Time"] = timestamp
                event["Zone"] = zone["name"]
                if trait == "sdm.devices.traits.Temperature":
                    event["Temperature"] = (
                        value["ambientTemperatureCelsius"] * 9 / 5 + 32
                    )
                elif trait == "sdm.devices.traits.Humidity":
                    event["Humidity"] = value["ambientHumidityPercent"]
                elif trait == "sdm.devices.traits.ThermostatHvac":
                    pass
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
        else:
            raise ValueError("Unexpected message format")
    return events


def load_weather_events():
    with open("weather-events.json", "r") as file:
        observations = json.load(file)
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
    return events


def load_events():
    events = load_nest_events()
    events.extend(load_weather_events())
    return events


def extract_trait(name, events):
    # select the events that have name as a key
    points = []
    for event in events:
        if name in event:
            points.append(event)
    return pd.DataFrame(points)


def plot_trait(name, events):
    df = extract_trait(name, events)
    plt.figure()
    sns.lineplot(x="Time", y=name, hue="Zone", data=df)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    file_name = f"{name}.png"
    plt.savefig(file_name, dpi=300, bbox_inches="tight", pad_inches=0.5)
    print(f"Plot: {file_name}")


events = load_events()
plot_trait("Temperature", events)
plot_trait("Humidity", events)
