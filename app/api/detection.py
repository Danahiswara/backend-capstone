from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.item import Item
from app.models.type import Type
from app.models.detection import Detection

from app.services.ai_service import detect_objects
from app.services.detection_service import save_detection
from app.services.type_service import get_type_by_name

router = APIRouter(prefix="/detection", tags=["Detection"])


@router.post("/{item_id}")
def run_detection(
    item_id: int,
    type_id: int,  # 🔥 dari user dropdown
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Item).filter(
        Item.item_id == item_id,
        Item.user_id == current_user.user_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing = db.query(Detection).filter(
        Detection.item_id == item_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Item already detected"
        )

    # 🔥 panggil AI
    result = detect_objects(item.image_path)

    # 🔥 ambil type langsung dari DB (bukan dari AI)
    type_data = db.query(Type).filter(Type.type_id == type_id).first()

    if not type_data:
        raise HTTPException(404, "Type not found")

    # 🔥 proses hasil AI
    total_count = result["counts"]["total"]

    # rata-rata confidence
    confidences = [d["confidence"] for d in result["detections"]]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0

    # TODO: nanti ini dari overlay generator
    mask_url = result.get("mask_url", item.image_path)

    detection = save_detection(
        db=db,
        item_id=item_id,
        type_id=type_data.type_id,
        mask_path=mask_url,
        object_count=total_count,
        confidence_score=avg_conf
    )

    return {
        "item_id": item_id,
        "type": type_data.name,
        "count": detection.object_count,
        "confidence_score": detection.confidence_score,
        "mask_url": detection.mask_path
    }