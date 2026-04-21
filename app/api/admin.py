from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.admin_service import (
    get_pending_users,
    approve_user,
    delete_user
)
from app.core.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


# 🔍 Get pending users
@router.get("/users/pending")
def pending_users(
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return get_pending_users(db)


# ✅ Approve user
@router.put("/users/{user_id}/approve")
def approve(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return approve_user(db, user_id)


# ❌ Delete user
@router.delete("/users/{user_id}")
def delete(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return delete_user(db, user_id)