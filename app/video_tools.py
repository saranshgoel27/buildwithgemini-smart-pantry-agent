import base64
import subprocess
import uuid

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


async def generate_item_video(
    item_name: str, tool_context: ToolContext
) -> str:
    """Generates a short video for a food item, recipe, or pantry ingredient using Google's Omni model (gemini-omni-flash-preview) in the global region, saves it to session artifacts, uploads it to Cloud Storage, and returns its public URL.

    Args:
        item_name: Name or description of the food item, recipe, or ingredient.

    Returns:
        The public HTTPS URL of the uploaded video in Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

    prompt = (
        f"A short 3-5 second clip showing {item_name} being fresh, beautifully prepared, "
        "or presented in a kitchen setting."
    )

    interaction = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=prompt,
    )

    vid = getattr(interaction, "output_video", None)
    if not vid and isinstance(interaction, dict):
        vid = interaction.get("output_video")
    if not vid:
        dump = interaction.model_dump() if hasattr(interaction, "model_dump") else {}
        vid = dump.get("output_video")

    if not vid:
        raise RuntimeError(
            f"Failed to generate video for '{item_name}' - no video output returned"
        )

    b64_data = getattr(vid, "data", None) if not isinstance(vid, dict) else vid.get("data")
    if not b64_data:
        raise RuntimeError(
            f"Generated video output contains no data for '{item_name}'"
        )

    mime_type = (
        getattr(vid, "mime_type", "video/mp4")
        if not isinstance(vid, dict)
        else vid.get("mime_type", "video/mp4")
    )
    if isinstance(b64_data, str):
        video_bytes = base64.b64decode(b64_data)
    else:
        video_bytes = b64_data

    safe_name = "".join(
        c for c in item_name.lower() if c.isalnum() or c == " "
    ).strip().replace(" ", "_")
    unique_id = uuid.uuid4().hex[:6]
    ext = "mp4"
    filename = f"{safe_name}_{unique_id}.{ext}"

    # 1. Save with tool_context.save_artifact for Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
        custom_metadata={"item_name": item_name},
    )

    # 2. Upload video bytes directly to Cloud Storage bucket (without writing to local file)
    storage_client = _get_storage_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url
