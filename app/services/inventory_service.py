from sqlalchemy.orm import Session
from app.models.item import Item

def create_item(db: Session, user_id: int, item_name: str, image_path: str):
    new_item = Item(
        user_id=user_id,
        item_name=item_name,
        image_path=image_path
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item
