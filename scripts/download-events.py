import yaml
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()


def fetch_and_save_collection(collection_name):
    """Fetches documents from a Firestore collection and saves them to a local
    YAML file.
    """
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()

    data = [doc.to_dict() for doc in docs]

    output_file = f"{collection_name}.yaml"
    with open(output_file, "w") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    print(f"Data saved to {output_file}")


if __name__ == "__main__":
    fetch_and_save_collection("nest-data-all")
