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


def load_data():
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
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())
    file_name = f"{name}.png"
    plt.savefig(file_name, dpi=300, bbox_inches="tight", pad_inches=0.5)
    print(f"Plot: {file_name}")


events = load_data()
plot_trait("Temperature", events)
plot_trait("Humidity", events)
