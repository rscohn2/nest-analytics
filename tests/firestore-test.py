from google.cloud import firestore

# Replace 'your-project-id' with your actual project ID
PROJECT_ID = "home-automation-428411"


def main():
    """Stores test data in a local Firestore instance."""

    # Create a Firestore client
    db = firestore.Client()

    # Create a document reference
    doc_ref = db.collection("test_data").document()

    # Create test data
    test_data = {
        "name": "Test Data",
        "value": 123,
        "timestamp": firestore.SERVER_TIMESTAMP,
    }

    # Store the data in Firestore
    doc_ref.set(test_data)

    print(f"Test data stored in Firestore: {test_data}")


if __name__ == "__main__":
    main()
