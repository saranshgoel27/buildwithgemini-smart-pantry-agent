import subprocess
from google.cloud import firestore
from google.oauth2 import credentials

# Hardcoded GCP Project ID as requested (never read from google.auth.default or GOOGLE_CLOUD_PROJECT)
PROJECT_ID = "qwiklabs-gcp-02-fa5a2915d776"


def get_firestore_client() -> firestore.Client:
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        creds = credentials.Credentials(token)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    except Exception as e:
        print(f"Warning: Falling back to default credentials ({e})")
        return firestore.Client(project=PROJECT_ID)


db = get_firestore_client()

ITEMS = [
    {
        "name": "Extra Virgin Olive Oil",
        "category": "Pantry",
        "quantity": 1.5,
        "unit": "liters",
        "expiration_date": "2027-01-15",
        "notes": "Cold pressed, organic",
    },
    {
        "name": "Basmati Rice",
        "category": "Grains",
        "quantity": 5.0,
        "unit": "kg",
        "expiration_date": "2027-06-30",
        "notes": "Aromatic long grain",
    },
    {
        "name": "Organic Large Eggs",
        "category": "Dairy",
        "quantity": 12.0,
        "unit": "eggs",
        "expiration_date": "2026-10-10",
        "notes": "Keep refrigerated",
    },
    {
        "name": "Whole Milk",
        "category": "Dairy",
        "quantity": 1.0,
        "unit": "gallon",
        "expiration_date": "2026-10-05",
        "notes": "Vitamin D fortified",
    },
    {
        "name": "San Marzano Canned Tomatoes",
        "category": "Canned Goods",
        "quantity": 4.0,
        "unit": "cans",
        "expiration_date": "2028-03-20",
        "notes": "Whole peeled 28oz cans",
    },
]


def seed():
    print(f"Seeding Firestore database in project: {PROJECT_ID}...")
    collection_ref = db.collection("pantry_items")
    for item in ITEMS:
        doc_id = item["name"].lower().replace(" ", "_")
        collection_ref.document(doc_id).set(item)
        print(f"  Added item: {item['name']} (ID: {doc_id})")
    print("Database seeding complete!")


if __name__ == "__main__":
    seed()
