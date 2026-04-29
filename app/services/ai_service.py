import requests
from app.core.config import settings
from app.services.mock_ai_service import mock_detect_objects
from app.utils.mask_overlay import generate_mask_overlay
from app.utils.supabase_upload import upload_mask_image


def detect_objects(image_url: str):

    if settings.USE_MOCK_AI:
        return mock_detect_objects(image_url)

    endpoint = f"{settings.AI_SERVICE_URL}/predict"

    response = requests.post(
        endpoint,
        json={"image_url": image_url}
    )

    if response.status_code != 200:
        raise Exception("AI service error")

    data = response.json()

    # =========================
    # 🔥 PROCESS RESULT
    # =========================
    detections = data["detections"]

    total_count = data["counts"]["total"]

    # rata-rata confidence
    avg_conf = sum(d["confidence"] for d in detections) / len(detections)

    # ambil class dominan
    type_name = max(
        data["counts"],
        key=lambda k: data["counts"][k] if k != "total" else -1
    )

    # generate mask overlay
    mask_img = generate_mask_overlay(image_url, detections)

    # upload ke supabase
    mask_url = upload_mask_image(mask_img)

    return {
        "type_name": type_name,
        "count": total_count,
        "confidence_score": round(avg_conf, 4),
        "mask_url": mask_url
    }