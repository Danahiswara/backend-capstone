from sqlalchemy.orm import Session
from app.models.detection import Detection
from datetime import datetime


def save_detection(
    db: Session,
    item_id: int,
    type_id: int,
    mask_path: str,
    object_count: int,
    confidence_score: int
):

    detection = Detection(
        item_id=item_id,
        type_id=type_id,
        mask_path=mask_path,
        object_count=object_count,
        confidence_score=confidence_score,
        detected_at=datetime.utcnow()
    )

    db.add(detection)
    db.commit()
    db.refresh(detection)

    return detection