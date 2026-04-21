from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.incoming_log import IncomingLog
from app.models.type import Type


def create_incoming(db: Session, type_id: int, quantity: int, user_id: int):
    if quantity <= 0:
        raise HTTPException(400, "Quantity must be greater than 0")

    type_data = db.query(Type).filter(Type.type_id == type_id).first()
    if not type_data:
        raise HTTPException(404, "Type not found")

    # tambah stok
    type_data.total_items += quantity

    incoming = IncomingLog(
        type_id=type_id,
        quantity=quantity,
        created_by=user_id
    )

    db.add(incoming)
    db.commit()
    db.refresh(incoming)

    return incoming