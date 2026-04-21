from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.outgoing_service import create_outgoing
from app.services.outgoing_service import create_outgoing_from_detection
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/outgoing", tags=["Outgoing"])


@router.post("/manual")
def outgoing_manual(
    type_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_outgoing(db, type_id, quantity, current_user.user_id, "manual")

@router.post("/ai")
def outgoing_ai(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_outgoing_from_detection(db, detection_id, current_user.user_id)