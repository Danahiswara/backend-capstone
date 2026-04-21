from supabase import create_client
from app.core.config import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)

def upload_image(file_bytes: bytes, filename: str):
    path = f"uploads/{filename}"

    supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        path,
        file_bytes
    )

    public_url = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(path)

    return public_url