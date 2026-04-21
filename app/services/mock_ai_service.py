import random
import uuid

types = ["kayu_gelondongan", "cabang_pohon", "pagar", "gantungan_baju", "antena", "kabel"]

def mock_detect_objects(image_url: str):

    fake_count = random.randint(15, 60)
    fake_mask_url = f"https://mock-storage/mask/{uuid.uuid4()}.png"

    return{
        "type_name": random.choice(types),
        "confidence_score": random.randint(10, 50),
        "count": fake_count,
        "mask_url": fake_mask_url
    }