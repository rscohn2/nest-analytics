from google.cloud import firestore

db = firestore.Client()

ref = db.collection("users").document("0").collection("nest-events")

for doc in ref.stream():
    doc.reference.update({"building": "1"})
    print(f"Document {doc.id} updated.")

print("Update complete.")
