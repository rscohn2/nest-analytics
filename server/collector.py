import base64
import json

import requests
from data_model import load_user
from flask import Blueprint, request
from ha_secrets import get_key

collector_blueprint = Blueprint("collector", __name__)

weather_name = "weather-events"
nest_name = "nest-events"


def store_event(user, event_type: str, event: dict) -> None:
    """Store event in firestore"""
    print(f"Storing {event_type} event {event}")
    doc_ref = user.data.collection(event_type).document()
    doc_ref.set(event)
    return


def fetch_weather(user) -> None:
    """Fetch and record weather data from OpenWeatherMap."""
    for building in user.buildings.values():
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?lat={building.latitude}&lon={building.longitude}"
            f"&appid={get_key('open-weather')}&units=metric"
        )
        response = requests.get(url)
        data = response.json()
        store_event(user, weather_name, data)


def hourly(user) -> None:
    """Triggered once an hour by scheduler module"""
    fetch_weather(user)


def decode_message(message):
    encoded_data = message["message"]["data"]
    data = base64.b64decode(encoded_data).decode()
    o = json.loads(data)
    return o


@collector_blueprint.route("/nest", methods=["POST"])
def nest_collector():
    """record information reported by thermostat"""
    if not request.json:
        return "Unsupported media type\n", 415
    print(f"Received nest event: {request.json}")
    store_event(nest_name, decode_message(request.json))
    return "Received nest event\n", 200


# For quick tests
if __name__ == "__main__":
    fetch_weather(load_user())
    pass
