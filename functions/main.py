import base64
import json

import functions_framework
import requests
from cloudevents.http import CloudEvent
from google.auth import default
from google.cloud import firestore, secretmanager

db = firestore.Client()


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
    """Fetch weather data from OpenWeatherMap."""
    # My house
    lat = "42.76950214174165"
    lon = "-71.27612488426918"
    api_key = get_secret("api-keys")["open-weather"]
    url = (
        "https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={api_key}&units=metric"
    )
    response = requests.get(url)
    data = response.json()
    store_event("weather_events", data)


@functions_framework.cloud_event
def hourly_events(cloud_event: CloudEvent) -> None:
    fetch_weather()


def decode_message(message):
    encoded_data = message["message"]["data"]
    data = base64.b64decode(encoded_data).decode()
    o = json.loads(data)
    return o


# We have manually created a push subscription to the nest events
# topic and provided the URL for this function. Events are posted to
# the URL.
@functions_framework.http
def process_webhook(request):
    """webhook provides event in request"""
    if request.method == "POST":
        store_event("nest_events", decode_message(request.get_json()))
        return "OK\n", 200
    else:
        return f"Unsupported method: {request.method}\n", 400


if __name__ == "__main__":
    fetch_weather()
    pass
