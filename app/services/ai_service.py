import requests
from app.core.config import settings
from app.services.mock_ai_service import mock_detect_objects


def detect_objects(image_url: str):

    if settings.USE_MOCK_AI:
        return mock_detect_objects(image_url)

    endpoint = f"{settings.AI_SERVICE_URL}/predict"

    response = requests.post(
        endpoint,
        json={
            "image_url": image_url
        }
    )

    if response.status_code != 200:
        raise Exception("AI service error")

    return response.json()
