import subprocess
import uuid
from typing import Optional

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types
from google.oauth2 import credentials

# Hardcoded GCP Project ID and Bucket Name as required
PROJECT_ID = "qwiklabs-gcp-02-fa5a2915d776"
BUCKET_NAME = "qwiklabs-gcp-02-fa5a2915d776-smart-pantry-media"


def _get_storage_client() -> storage.Client:
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        creds = credentials.Credentials(token)
        return storage.Client(project=PROJECT_ID, credentials=creds)
    except Exception:
        return storage.Client(project=PROJECT_ID)


async def generate_item_image(
    item_name: str, tool_context: ToolContext
) -> str:
    """Generates an image of a food item, recipe, or pantry ingredient using AI,
    saves it to session artifacts, uploads it to Cloud Storage, and returns its public URL.

    Args:
        item_name: Name or description of the food item, recipe, or ingredient.

    Returns:
        The public HTTPS URL of the uploaded image in Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

    prompt = (
        f"A high quality studio food photograph of {item_name}, beautifully presented "
        "on a wooden kitchen counter or serving plate."
    )

    res = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )

    if (
        not res.candidates
        or not res.candidates[0].content
        or not res.candidates[0].content.parts
    ):
        raise RuntimeError(f"Failed to generate image for '{item_name}'")

    image_part = res.candidates[0].content.parts[0]
    if not image_part.inline_data or not image_part.inline_data.data:
        raise RuntimeError(
            f"Generated image part has no inline data for '{item_name}'"
        )

    image_bytes = image_part.inline_data.data
    mime_type = image_part.inline_data.mime_type or "image/jpeg"

    ext = "png" if "png" in mime_type.lower() else "jpg"
    safe_name = "".join(c for c in item_name.lower() if c.isalnum() or c == " ").strip().replace(" ", "_")
    unique_id = uuid.uuid4().hex[:6]
    filename = f"{safe_name}_{unique_id}.{ext}"

    # 1. Save with tool_context.save_artifact for Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
        custom_metadata={"item_name": item_name},
    )

    # 2. Upload image bytes directly to Cloud Storage bucket (without writing to local file)
    storage_client = _get_storage_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url
