import argparse

import yaml
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()


def fetch_and_save_collection(collection_path):
    """Fetches documents from a Firestore collection and saves them to a local
    YAML file.
    """
    collection_ref = db.collection(collection_path)
    docs = collection_ref.stream()

    data = [doc.to_dict() for doc in docs]

    collection_name = collection_path.split("/")[-1]
    output_file = f"{collection_name}.yaml"
    with open(output_file, "w") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    print(
        f"{collection_name} collection with {len(data)} documents"
        f" saved to {output_file}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download firestore collection."
    )
    parser.add_argument(
        "collection_path",
        help="The path of the Firestore collection to fetch.",
    )
    args = parser.parse_args()
    fetch_and_save_collection(args.collection_path)
