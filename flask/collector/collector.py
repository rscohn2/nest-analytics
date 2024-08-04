import base64
import json

import requests
from common.data_model import Structure, db
from common.secrets import get_key

from flask import Blueprint, abort, current_app, request

collector_blueprint = Blueprint("collector", __name__)

weather_name = "weather-events"
nest_name = "nest-events"


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


def decode_message(message):
    encoded_data = message["message"]["data"]
    data = base64.b64decode(encoded_data).decode()
    o = json.loads(data)
    return o


@collector_blueprint.route("/nest", methods=["POST"])
def nest_collector():
    """Record information reported by thermostat"""
    token = request.args.get("token", default=None, type=str)
    if not token or token != current_app.secret_key:
        print("aborting")
        abort(403)

    if not request.json:
        return "Unsupported media type\n", 415

    return "Received nest event\n", 200
