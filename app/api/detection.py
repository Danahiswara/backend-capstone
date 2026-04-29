from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.item import Item
from app.models.detection import Detection

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

    result = detect_objects(item.image_path)

    # =========================
    # VALIDASI TYPE
    # =========================
    type_data = get_type_by_name(db, result["type_name"])

    if not type_data:
        raise HTTPException(
            status_code=400,
            detail=f"Type '{result['type_name']}' not found in database"
        )

    # =========================
    # SAVE
    # =========================
    detection = save_detection(
        db=db,
        item_id=item_id,
        type_id=type_data.type_id,
        mask_path=result["mask_url"],
        object_count=result["count"],
        confidence_score=result["confidence_score"]
    )

    return {
        "item_id": item_id,
        "type": type_data.name,
        "count": detection.object_count,
        "confidence_score": detection.confidence_score,
        "mask_url": detection.mask_path
    }