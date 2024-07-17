import base64
import json

import requests
from common.data_model import load_user
from common.secrets import get_key

from flask import Blueprint, abort, request

collector_blueprint = Blueprint("collector", __name__)

weather_name = "weather-events"
nest_name = "nest-events"


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
        user.store_event(weather_name, data)


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
    """Record information reported by thermostat"""
    token = request.args.get("token", default=None, type=str)
    if not token or token != get_key("ha-service"):
        print("aborting")
        abort(403)

    if not request.json:
        return "Unsupported media type\n", 415

    user = load_user(0)
    user.store_event(nest_name, decode_message(request.json))
    return "Received nest event\n", 200


# For quick tests
if __name__ == "__main__":
    pass
