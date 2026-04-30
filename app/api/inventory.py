from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.inventory_service import create_item
from app.services.storage_service import upload_image
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.item import Item
from app.models.detection import Detection
from app.schemas.item import ItemResponse
import uuid
import os

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/upload", response_model=ItemResponse)
async def upload_item(
    item_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generate unique filename
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"

    file_bytes = await file.read()

    image_url = upload_image(file_bytes, filename)

    # Simpan ke database
    item = create_item(
        db=db,
        user_id=current_user.user_id,
        item_name=item_name,
        image_path=image_url
    )

    return item

@router.get("/my-items")
def get_my_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    results = (
        db.query(Item, Detection)
        .join(Detection, Detection.item_id == Item.item_id)
        .filter(Item.user_id == current_user.user_id)
        .all()
    )

    response = []

    for item, detection in results:
        response.append({
            "item_id": item.item_id,
            "detection_id": detection.detection_id,
            "image": item.image_path,
            "mask": detection.mask_path,
            "object_count": detection.object_count,
            "confidence_score": detection.confidence_score,
            "created_at": item.created_at
        })

    return response