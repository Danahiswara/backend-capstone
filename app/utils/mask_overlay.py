import requests
import numpy as np
import cv2
from PIL import Image
from io import BytesIO


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
    # download image
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content)).convert("RGB")

    image = resize_like_model(image)

    img = np.array(image)

    overlay = img.copy()

    for det in detections:
        bbox = det["bbox"]

        x1 = int(bbox["x1"])
        y1 = int(bbox["y1"])
        x2 = int(bbox["x2"])
        y2 = int(bbox["y2"])

        # warna mask (hijau transparan)
        color = (0, 255, 0)

        # gambar rectangle sebagai mask sederhana
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)

    # blend (transparansi)
    alpha = 0.3
    result = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    return result