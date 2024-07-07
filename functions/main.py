import base64
import json

import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import firestore


def store_event(event: dict) -> None:
    """Store event in firestore"""
    print(f"Storing event {event}")
    db = firestore.Client()
    doc_ref = db.collection("nest_events").document()
    doc_ref.set(event)
    return


def decode_message(message):
    encoded_data = message["message"]["data"]
    data = base64.b64decode(encoded_data).decode()
    o = json.loads(data)
    return o


# Cloud functions can automatically create a push subscription to a
# pubsub topic, but it requires that the topic and function are in the
# same project. The topic is created by nest service and is in a
# different project.
@functions_framework.cloud_event
def process_message(cloud_event: CloudEvent) -> None:
    pubsub_message = base64.b64decode(
        cloud_event.data["message"]["data"]
    ).decode()
    store_event(json.loads(pubsub_message))
    return


# We have manually created a push subscription to the nest events
# topic and provided the URL for this function. Events are posted to
# the URL.
@functions_framework.http
def process_webhook(request):
    """webhook provides event in request"""
    if request.method == "POST":
        store_event(decode_message(request.get_json()))
        return "OK\n", 200
    else:
        return f"Unsupported method: {request.method}\n", 400


if __name__ == "__main__":
    pass
