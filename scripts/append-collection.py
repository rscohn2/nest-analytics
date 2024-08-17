import sys

import yaml
from google.cloud import firestore


def read_yaml(file_path):
    """Reads a YAML file and returns the content."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def add_to_firestore(data, collection_path):
    """Adds a list of dictionaries to a Firestore collection."""
    db = firestore.Client()
    collection_ref = db.collection(collection_path)
    batch = db.batch()

    for item in data:
        doc_ref = collection_ref.document()
        batch.set(doc_ref, item)
    batch.commit()
    print(f"Added {len(data)} documents to: {collection_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py  <collection_path> <filename>")
        sys.exit(1)

    collection_path = sys.argv[1]
    filename = sys.argv[2]

    # Read the YAML file
    data = read_yaml(filename)

    # Add data to Firestore
    add_to_firestore(data, collection_path)
