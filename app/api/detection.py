from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.item import Item
from app.models.type import Type
from app.models.detection import Detection

from app.utils.mask_overlay import generate_mask_overlay
from app.utils.supabase_upload import upload_mask_image

from app.services.ai_service import detect_objects
from app.services.detection_service import save_detection
from app.services.type_service import get_type_by_name

router = APIRouter(prefix="/detection", tags=["Detection"])


@router.post("/{item_id}")
def run_detection(
    item_id: int,
    type_id: int,  # 🔥 dari user (QUERY PARAM / FORM)
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ======================
    # VALIDASI ITEM
    # ======================
    item = db.query(Item).filter(
        Item.item_id == item_id,
        Item.user_id == current_user.user_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    # ======================
    # VALIDASI TYPE (PENTING)
    # ======================
    type_data = db.query(Type).filter(
        Type.type_id == type_id
    ).first()

    if not type_data:
        raise HTTPException(404, "Type not found")

    # ======================
    # CEK DUPLIKAT DETEKSI
    # ======================
    existing = db.query(Detection).filter(
        Detection.item_id == item_id
    ).first()

    if existing:
        raise HTTPException(400, "Item already detected")

    # ======================
    # CALL AI
    # ======================
    result = detect_objects(item.image_path)

    if not result:
        raise HTTPException(500, "AI service error")

    detections = result.get("detections", [])

    # ======================
    # OBJECT COUNT
    # ======================
    object_count = result.get("total_detections") \
        or result.get("counts", {}).get("total", 0)

    # ======================
    # AVG CONFIDENCE
    # ======================
    if detections:
        confidences = [d.get("confidence", 0) for d in detections]
        avg_conf = sum(confidences) / len(confidences)
    else:
        avg_conf = 0

    # ======================
    # GENERATE MASK
    # ======================
    overlay = generate_mask_overlay(
        item.image_path,
        detections
    )

    mask_url = upload_mask_image(overlay)

    # ======================
    # SAVE
    # ======================
    detection = save_detection(
        db=db,
        item_id=item_id,
        type_id=type_id,  # 🔥 dari user
        mask_path=mask_url,
        object_count=int(object_count),
        confidence_score=float(avg_conf)
    )

    return {
        "item_id": item_id,
        "type_id": detection.type_id,
        "count": detection.object_count,
        "confidence_score": round(detection.confidence_score, 4),
        "mask_url": detection.mask_path
    }