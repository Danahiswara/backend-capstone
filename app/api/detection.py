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
    # CEK SUDAH ADA DETEKSI
    # ======================
    existing = db.query(Detection).filter(
        Detection.item_id == item_id
    ).first()

    if existing:
        raise HTTPException(400, "Item already detected")

    # ======================
    # CALL AI SERVICE
    # ======================
    result = detect_objects(item.image_path)

    if not result:
        raise HTTPException(500, "AI service error")

    # ======================
    # AMBIL DATA DETEKSI
    # ======================
    detections = result.get("detections", [])

    # ======================
    # OBJECT COUNT (FIX)
    # ======================
    object_count = result.get("total_detections") \
        or result.get("counts", {}).get("total", 0)

    # ======================
    # AVG CONFIDENCE
    # ======================
    if detections:
        confidences = [d.get("confidence", 0) for d in detections]
        avg_confidence = sum(confidences) / len(confidences)
    else:
        avg_confidence = 0

    # ======================
    # TYPE DARI USER (ITEM)
    # ======================
    type_data = db.query(Type).filter(
        Type.type_id == detection.type_id
    ).first()

    if not type_data:
        raise HTTPException(400, "Type not found")

    # ======================
    # GENERATE MASK OVERLAY
    # ======================
    try:
        overlay_image = generate_mask_overlay(
            item.image_path,
            detections
        )
    except Exception as e:
        raise HTTPException(500, f"Mask generation failed: {str(e)}")

    # ======================
    # UPLOAD KE SUPABASE
    # ======================
    try:
        mask_url = upload_mask_image(overlay_image)
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

    # ======================
    # SAVE KE DATABASE
    # ======================
    detection = save_detection(
        db=db,
        item_id=item_id,
        type_id=type_data.type_id,
        mask_path=mask_url,
        object_count=int(object_count),
        confidence_score=float(avg_confidence)
    )

    # ======================
    # RESPONSE
    # ======================
    return {
        "item_id": item_id,
        "type": type_data.name,
        "count": detection.object_count,
        "confidence_score": round(detection.confidence_score, 4),
        "mask_url": detection.mask_path
    }