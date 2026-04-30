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

router = APIRouter(prefix="/detection", tags=["Detection"])


@router.post("/{item_id}")
def run_detection(
    item_id: int,
    type_id: int,
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
    # VALIDASI TYPE
    # ======================
    type_data = db.query(Type).filter(
        Type.type_id == type_id
    ).first()

    if not type_data:
        raise HTTPException(404, "Type not found")

    # ======================
    # CEK DUPLIKAT
    # ======================
    existing = db.query(Detection).filter(
        Detection.item_id == item_id
    ).first()

    if existing:
        raise HTTPException(400, "Item already detected")

    # ======================
    # CALL AI (SUDAH FINAL)
    # ======================
    result = detect_objects(item.image_path)

    if not result:
        raise HTTPException(500, "AI service failed")

    # ======================
    # SAVE
    # ======================
    detection = save_detection(
        db=db,
        item_id=item_id,
        type_id=type_id,
        mask_path=result["mask_url"],
        object_count=result["count"],
        confidence_score=result["confidence_score"]
    )

    return {
        "detection_id": detection.detection_id,
        "item_id": item_id,
        "type_id": detection.type_id,
        "count": detection.object_count,
        "confidence_score": detection.confidence_score,
        "mask_url": detection.mask_path
    }