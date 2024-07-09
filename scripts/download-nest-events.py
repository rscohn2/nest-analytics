import json

from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()


def fetch_and_save_collection(collection_name, output_file):
    """Fetches documents from a Firestore collection and saves them to a local
    JSON file.
    """
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()

    data = [doc.to_dict() for doc in docs]

    with open(output_file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # Specify the Firestore collection name and output file path
    collection_name = "nest_events"
    output_file = "nest-events.json"
    fetch_and_save_collection(collection_name, output_file)
