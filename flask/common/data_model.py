import uuid

import portal.globals as globals
import yaml
from flask_login import UserMixin
from google.cloud import firestore

from flask import current_app

db = firestore.Client()


def extract_id(name, key):
    parts = name.split("/")
    for i in range(0, len(parts) - 1, 2):
        if parts[i] == key:
            return parts[i + 1]
    return None


def room_name(device):
    for p in device["parentRelations"]:
        name = p.get("displayName")
        if name:
            return name
    return None


class Device:
    def __init__(self, attributes: dict):
        for key, value in attributes.items():
            setattr(self, key, value)

    def __str__(self):
        return yaml.dump(self.__dict__)


class Structure:
    def __init__(self, data: dict):
        # make the common data attributes
        for attr in ["owner_id", "address", "latitude", "longitude"]:
            setattr(self, attr, data.get(attr))
        # everything else as a dictionary
        self.name = data["traits"]["sdm.structures.traits.Info"]["customName"]
        self.id = extract_id(data["name"], "structures")
        self.rooms = data["rooms"]
        self.aux = data

    def save(self):
        self.aux["address"] = self.address
        self.aux["latitude"] = self.latitude
        self.aux["longitude"] = self.longitude
        db.collection("structures").document(self.id).set(self.aux)

    @staticmethod
    def all_structures():
        """Returns all structures. Does not filter by user"""
        return [
            Structure(doc.to_dict())
            for doc in db.collection("structures").stream()
        ]

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
        self.structures = self.get_structures()
        self.current_structure = (
            self.structures[0] if len(self.structures) > 0 else None
        )
        self.data = db.collection("users").document(self.profile.id)

    def __str__(self):
        return yaml.dump(self.__dict__)

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

    def get_structures(self):
        s = (
            db.collection("structures")
            .where("owner_id", "==", self.id)
            .stream()
        )
        return [Structure(doc.to_dict()) for doc in s]

    def link_nest(self):
        structures = {}
        for structure in self.list_resource("structures")["structures"]:
            # add to db
            structure["owner_id"] = self.id
            doc_name = extract_id(structure["name"], "structures")
            old_ref = db.collection("structures").document(doc_name).get()
            old = old_ref.to_dict()
            # copy some fields from old doc
            if old_ref.exists:
                for key in ["address", "latitude", "longitude", "rooms"]:
                    if key in old:
                        structure[key] = old[key]
            if "rooms" not in structure:
                structure["rooms"] = {}
            structures[doc_name] = structure

        for device in self.list_resource("devices")["devices"]:
            assignee = device["assignee"]
            structure_id = extract_id(assignee, "structures")
            room_id = extract_id(assignee, "rooms")
            device_id = extract_id(device["name"], "devices")
            structure = structures[structure_id]
            room = structure["rooms"].get(room_id)
            if not room:
                room = {
                    "name": room_name(device),
                    "id": room_id,
                    "devices": {},
                }
                structure["rooms"][room_id] = room
            old_device = room.get(device_id)
            if not old_device:
                room["devices"][device_id] = device
        print(
            f"Structures:\n{yaml.dump(structures, default_flow_style=False)}"
        )

        for id, structure in structures.items():
            db.collection("structures").document(id).set(structure)


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


def load_user_by_userinfo(userinfo: dict) -> User:
    users_ref = db.collection("users")
    query = users_ref.where("profile.email", "==", userinfo["email"]).stream()
    for user in query:
        return User(user.to_dict())

    # not found, create user
    return User.create(userinfo)


if __name__ == "__main__":
    pass
