from sqlalchemy.orm import Session
from app.models.item import Item
from typing import Optional

def create_item(db: Session, user_id: int, item_name: Optional [str] = None, image_path: str = None):
    new_item = Item(
        user_id=user_id,
        item_name=item_name,
        image_path=image_path
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item
