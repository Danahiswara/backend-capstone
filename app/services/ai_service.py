import requests
from app.core.config import settings
from app.utils.mask_overlay import generate_mask_overlay
from app.utils.supabase_upload import upload_mask_image


def detect_objects(image_url: str):
    endpoint = f"{settings.AI_SERVICE_URL}/predict"

    # =========================
    # DOWNLOAD IMAGE
    # =========================
    img_response = requests.get(image_url)

    if img_response.status_code != 200:
        raise Exception("Failed to download image")

    files = {
        "file": ("image.jpg", img_response.content, "image/jpeg")
    }

    # =========================
    # SEND TO AI (multipart)
    # =========================
    response = requests.post(
        endpoint,
        files=files,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"AI service error: {response.text}")

    data = response.json()

    # =========================
    # SAFE PARSING
    # =========================
    detections = data.get("detections", [])

    total_count = (
        data.get("total_detections")
        or data.get("counts", {}).get("total")
        or len(detections)
        or 0
    )

    # =========================
    # CONFIDENCE
    # =========================
    if detections:
        avg_conf = sum(d.get("confidence", 0) for d in detections) / len(detections)
    else:
        avg_conf = 0.0

    # =========================
    # MASK
    # =========================
    try:
        mask_img = generate_mask_overlay(image_url, detections)
        mask_url = upload_mask_image(mask_img)
    except Exception as e:
        print("MASK ERROR:", str(e))
        mask_url = None

    return {
        "count": int(total_count),
        "confidence_score": round(avg_conf, 4),
        "mask_url": mask_url
    }