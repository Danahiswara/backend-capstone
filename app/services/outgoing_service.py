from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.outgoing_log import OutgoingLog
from app.models.type import Type
from app.models.detection import Detection


def create_outgoing(db: Session, type_id: int, quantity: int, user_id: int, method: str, detection_id: int = None):
    if quantity <= 0:
        raise HTTPException(400, "Quantity must be greater than 0")

    type_data = db.query(Type).filter(Type.type_id == type_id).first()
    if not type_data:
        raise HTTPException(404, "Type not found")

    # VALIDASI STOCK
    if quantity > type_data.total_items:
        raise HTTPException(400, "Stock not enough")

    # kurangi stok
    type_data.total_items -= quantity

    outgoing = OutgoingLog(
        type_id=type_id,
        quantity=quantity,
        method=method,
        detection_id=detection_id,
        created_by=user_id
    )

    db.add(outgoing)
    db.commit()
    db.refresh(outgoing)

    return outgoing

def create_outgoing_from_detection(db: Session, detection_id: int, user_id: int):
    detection = db.query(Detection).filter(Detection.detection_id == detection_id).first()

    if not detection:
        raise HTTPException(404, "Detection not found")

    quantity = detection.object_count
    type_id = detection.type_id
    detection_id = detection.detection_id

    return create_outgoing(db, type_id, quantity, user_id, method="ai", detection_id=detection.detection_id)