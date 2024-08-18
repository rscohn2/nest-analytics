import json

import requests
import yaml
from common.data_model import Structure, db
from common.secrets import current_project_id, get_key
from google.cloud import pubsub_v1


def filter_event(event, temperatures, humidities):
    resource = event.get("resourceUpdate")
    if not resource:
        return True

    thermostat = resource["name"]
    traits = resource["traits"]

    trait_v = traits.get("sdm.devices.traits.Temperature")
    if trait_v:
        previous = temperatures.get(thermostat)
        current = trait_v["ambientTemperatureCelsius"]
        if previous and abs(current - previous) < 0.25:
            return False
        temperatures[thermostat] = current
        return True

    trait_v = traits.get("sdm.devices.traits.Humidity")
    if trait_v:
        previous = humidities.get(thermostat)
        current = trait_v["ambientHumidityPercent"]
        if previous and abs(current - previous) < 1:
            return False
        humidities[thermostat] = current
        return True

    return True


def fetch_nest() -> None:
    """Pull nest subscription and record."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        current_project_id(), "nest-pull"
    )
    response = subscriber.pull(
        request={
            "subscription": subscription_path,
            "max_messages": 500,
        }
    )

    temperatures = {}
    humidities = {}
    ack_ids = []
    batch = db.batch()
    for received_message in response.received_messages:
        print(f"Received message: {received_message.message.data}")
        data = json.loads(received_message.message.data.decode("utf-8"))
        batch.set(db.collection("nest-data-all").document(), data)
        if filter_event(data, temperatures, humidities):
            batch.set(db.collection("nest-data").document(), data)
        ack_ids.append(received_message.ack_id)
    batch.commit()

    # Acknowledge the received messages so they will not be sent again.
    subscriber.acknowledge(
        request={
            "subscription": subscription_path,
            "ack_ids": ack_ids,
        }
    )


def fetch_weather() -> None:
    """Fetch and record weather data from OpenWeatherMap."""
    for s in Structure.all_structures():
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?lat={s.latitude}&lon={s.longitude}"
            f"&appid={get_key('open-weather')}&units=metric"
        )
        response = requests.get(url)
        data = response.json()
        data["structure"] = s.id
        db.collection("weather-data").add(data)


def hourly() -> None:
    """Triggered once an hour by scheduler module"""
    fetch_weather()
    fetch_nest()


def load_events_from_yaml(file_path: str) -> None:
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    temperatures = {}
    humidities = {}
    events = load_events_from_yaml("nest-data-all.yaml")
    for event in events:
        print(f"{yaml.dump(event)}")
        if not filter_event(event, temperatures, humidities):
            print("Discard")
