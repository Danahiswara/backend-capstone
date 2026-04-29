import uuid
import cv2
from app.core.config import settings
from supabase import create_client

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def upload_mask_image(image_np):
    filename = f"mask/{uuid.uuid4()}.jpg"

    _, buffer = cv2.imencode(".jpg", image_np)

    supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        filename,
        buffer.tobytes(),
        {"content-type": "image/jpeg"}
    )

    public_url = supabase.storage.from_(settings.SUPABASE_BUCKET)\
        .get_public_url(filename)

    return public_url