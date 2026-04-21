from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.incoming_service import create_incoming
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/incoming", tags=["Incoming"])


@router.post("/")
def add_incoming(
    type_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_incoming(db, type_id, quantity, current_user.user_id)