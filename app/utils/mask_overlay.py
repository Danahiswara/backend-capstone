import requests
import numpy as np
import cv2
import random
from PIL import Image
from io import BytesIO

def random_color():
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )

def resize_like_model(image: Image.Image, max_size=800):
    W, H = image.size
    longest = max(W, H)

    if longest <= max_size:
        return image

    scale = max_size / longest
    new_w = int(W * scale)
    new_h = int(H * scale)

    return image.resize((new_w, new_h), Image.BILINEAR)

def generate_mask_overlay(image_url: str, detections: list):
    # DOWNLOAD IMAGE
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    img = np.array(image)

    overlay = img.copy()

    # LOOP OBJECT (INSTANCE)
    for det in detections:
        polygon = det.get("polygon")

        if not polygon:
            continue

        # convert ke numpy
        pts = np.array(polygon, dtype=np.int32).reshape((-1, 1, 2))

        # warna random per object
        color = random_color()

        # DRAW FILLED MASK
        cv2.fillPoly(overlay, [pts], color)

        # OPTIONAL: OUTLINE
        cv2.polylines(overlay, [pts], True, (0, 0, 0), 2)

    # BLEND DENGAN IMAGE ASLI
    alpha = 0.4
    result = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    return result