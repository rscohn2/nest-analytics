import uuid

import portal.globals as globals
import yaml
from flask_login import UserMixin
from google.cloud import firestore

from flask import current_app

db = firestore.Client()


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


class Profile:
    def __init__(self, data: dict):
        # make the common data attributes
        for attr in ["id", "session_id", "email", "nest_token"]:
            setattr(self, attr, data.get(attr))
        # everything else as a dictionary
        self.aux = data

    def __str__(self):
        return yaml.dump(self.__dict__)


class User(UserMixin):
    def __init__(self, data: dict):
        self.profile = Profile(data["profile"])
        self.id = self.profile.id
        self.data = db.collection("users").document(self.profile.id)
        self.buildings = []

    def __str__(self):
        return yaml.dump(self.__dict__)

    def store_event(self, event_type: str, event: dict) -> None:
        doc_ref = self.data.collection(event_type).document()
        doc_ref.set(event)
        return

    def check_password(self, password):
        return password == current_app.secret_key

    # create from google userinfo
    def create(userinfo: dict):
        # this changes when the password changes to invalidate all sessions
        userinfo["session_id"] = str(uuid.uuid4())
        # this never changes
        userinfo["id"] = str(uuid.uuid4())
        user = {"profile": userinfo}
        db.collection("users").add(user, userinfo["id"])
        return User(user)

    def update_profile(self, name, value):
        self.data.update({f"profile.{name}": value})

    def list_resource(self, resource):
        resp = globals.oauth.nest.get(resource, token=self.profile.nest_token)
        resp.raise_for_status()
        data = resp.json()
        print(f"{resource} {data}")
        return data


def add_guids(guid, data):
    if isinstance(data, dict):
        if "guid" not in data and guid.isdigit():
            data["guid"] = guid
        for key, value in data.items():
            add_guids(key, value)


def load_user(id):
    doc_ref = db.collection("users").document(id)
    doc = doc_ref.get()
    if doc.exists:
        return User(doc.to_dict())
    return None


def load_user_by_username(username):
    u = load_user("0")
    if u.username == username:
        return u
    return None


def load_user_by_userinfo(userinfo: dict) -> User:
    users_ref = db.collection("users")
    query = users_ref.where("profile.email", "==", userinfo["email"]).stream()
    for user in query:
        return User(user.to_dict())

    # not found, create user
    return User.create(userinfo)


if __name__ == "__main__":
    pass
