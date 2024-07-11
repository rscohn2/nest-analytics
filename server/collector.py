import base64
import json

import requests
from flask import Blueprint, request
from google.auth import default
from google.cloud import firestore, secretmanager
from user import active_user

collector_blueprint = Blueprint("collector", __name__)

db = firestore.Client()

weather_name = "weather-events-test"
nest_name = "nest-events-test"


def store_event(event_type: str, event: dict) -> None:
    """Store event in firestore"""
    print(f"Storing {event_type} event {event}")
    doc_ref = db.collection(event_type).document()
    doc_ref.set(event)
    return


def current_project_id():
    _, project_id = default()
    if project_id is None:
        raise Exception(
            "Project ID could not be determined from the environment."
        )
    return project_id


def get_secret(secret_id: str) -> dict:
    """Retrieve a secret from Google Secret Manager and deserialize it."""
    client = secretmanager.SecretManagerServiceClient()
    name = (
        f"projects/{current_project_id()}/"
        f"secrets/{secret_id}/versions/latest"
    )
    response = client.access_secret_version(request={"name": name})
    secret_data = response.payload.data.decode("UTF-8")
    return json.loads(secret_data)


def fetch_weather() -> None:
    """Fetch and record weather data from OpenWeatherMap."""
    api_key = get_secret("api-keys")["open-weather"]
    for building in active_user.buildings.values():
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?lat={building.latitude}&lon={building.longitude}"
            f"&appid={api_key}&units=metric"
        )
        response = requests.get(url)
        data = response.json()
        store_event(weather_name, data)


def hourly() -> None:
    """Triggered once an hour by scheduer module"""
    fetch_weather()


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
    fetch_weather()
    pass
