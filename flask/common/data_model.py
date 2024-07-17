from os import environ

import yaml
from google.cloud import firestore


class Device:
    def __init__(self, attributes: dict):
        for key, value in attributes.items():
            setattr(self, key, value)

    def __str__(self):
        return yaml.dump(self.__dict__)


class Building:
    def __init__(self, attributes: dict):
        for b_key, b_value in attributes.items():
            if b_key == "devices":
                self.devices = {}
                for d_key, d_value in b_value.items():
                    self.devices[d_key] = Device(d_value)
            else:
                setattr(self, b_key, b_value)

    def __str__(self):
        return yaml.dump(self.__dict__)


class User:
    def __init__(self, attributes: dict):
        for u_key, u_value in attributes.items():
            if u_key == "buildings":
                self.buildings = {}
                for b_key, b_value in u_value.items():
                    self.buildings[b_key] = Building(b_value)
            else:
                setattr(self, u_key, u_value)
        db = firestore.Client()
        if environ.get("HA_TEST_DB"):
            self.data = (
                db.document("TEST").collection("users").document(self.guid)
            )
        else:
            self.data = db.collection("users").document(self.guid)

    def __str__(self):
        return yaml.dump(self.__dict__)

    def store_event(self, event_type: str, event: dict) -> None:
        doc_ref = self.data.collection(event_type).document()
        doc_ref.set(event)
        return


def add_guids(guid, data):
    if isinstance(data, dict):
        if "guid" not in data and guid.isdigit():
            data["guid"] = guid
        for key, value in data.items():
            add_guids(key, value)


def load_user(guid):
    with open("user_data.yaml", "r") as file:
        user = yaml.safe_load(file)
    add_guids("0", user)
    return User(user)


if __name__ == "__main__":
    pass
