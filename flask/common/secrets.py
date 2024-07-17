import json

from google.auth import default
from google.cloud import secretmanager


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


def get_key(key_name: str) -> str:
    return get_secret("api-keys")[key_name]
