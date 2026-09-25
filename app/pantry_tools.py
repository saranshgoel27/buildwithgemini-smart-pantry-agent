import datetime
import subprocess
from typing import Any, Dict, List, Optional
from google.cloud import firestore
from google.oauth2 import credentials

# Hardcoded GCP Project ID as requested (never read from google.auth.default or GOOGLE_CLOUD_PROJECT)
PROJECT_ID = "qwiklabs-gcp-02-fa5a2915d776"


def _get_firestore_client() -> firestore.Client:
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        creds = credentials.Credentials(token)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    except Exception:
        return firestore.Client(project=PROJECT_ID)


db = _get_firestore_client()


def list_pantry_items(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves pantry inventory items from the Firestore database.

    Args:
        category: Optional category filter (e.g. 'Pantry', 'Dairy', 'Grains', 'Canned Goods').

    Returns:
        A list of dictionary objects representing items in the pantry.
    """
    collection_ref = db.collection("pantry_items")
    if category:
        docs = collection_ref.where("category", "==", category).stream()
    else:
        docs = collection_ref.stream()

    items = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        items.append(data)
    return items


def check_expiring_pantry_items(days_threshold: int = 7) -> List[Dict[str, Any]]:
    """Checks pantry inventory for items that are expired or expiring within the specified number of days.

    Args:
        days_threshold: Number of days ahead to check for expiration (default 7 days).

    Returns:
        A list of items expiring or already expired within the threshold.
    """
    today = datetime.date.today()
    target_date = today + datetime.timedelta(days=days_threshold)

    docs = db.collection("pantry_items").stream()
    expiring = []

    for doc in docs:
        data = doc.to_dict()
        exp_str = data.get("expiration_date")
        if not exp_str:
            continue
        try:
            exp_date = datetime.datetime.strptime(exp_str, "%Y-%m-%d").date()
            if exp_date <= target_date:
                data["id"] = doc.id
                data["days_until_expiration"] = (exp_date - today).days
                expiring.append(data)
        except ValueError:
            continue

    return expiring


def add_or_update_pantry_item(
    name: str,
    category: str,
    quantity: float,
    unit: str,
    expiration_date: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Adds a new item or updates an existing item in the pantry inventory.

    Args:
        name: Name of the item (e.g. 'Whole Milk', 'Basmati Rice').
        category: Category (e.g. 'Dairy', 'Grains', 'Pantry', 'Produce').
        quantity: Quantity amount (e.g. 2.0).
        unit: Unit of measurement (e.g. 'liters', 'kg', 'cans', 'eggs').
        expiration_date: Optional expiration date in YYYY-MM-DD format.
        notes: Optional additional notes or description.

    Returns:
        A confirmation string indicating the item was added or updated.
    """
    doc_id = name.lower().strip().replace(" ", "_")
    item_data = {
        "name": name,
        "category": category,
        "quantity": float(quantity),
        "unit": unit,
        "expiration_date": expiration_date or "",
        "notes": notes or "",
    }
    db.collection("pantry_items").document(doc_id).set(item_data)
    return f"Successfully saved '{name}' in pantry inventory (ID: {doc_id})."


def remove_pantry_item(name: str) -> str:
    """Removes an item from the pantry inventory.

    Args:
        name: Name of the item to remove.

    Returns:
        A confirmation string indicating the item was deleted.
    """
    doc_id = name.lower().strip().replace(" ", "_")
    doc_ref = db.collection("pantry_items").document(doc_id)
    if not doc_ref.get().exists:
        return f"Item '{name}' not found in pantry inventory."

    doc_ref.delete()
    return f"Successfully removed '{name}' from pantry inventory."
