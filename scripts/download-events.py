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
    print(f"Data saved to {output_file}")


if __name__ == "__main__":
    fetch_and_save_collection("nest_events", "nest-events.json")
    fetch_and_save_collection("weather_events", "weather-events.json")
