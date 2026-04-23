from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.admin_service import (
    get_pending_users,
    approve_user,
    delete_user,
    reject_user,
    get_approved_petugas
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


@router.put("/users/{user_id}/reject")
def reject(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return reject_user(db, user_id)


# ✅ Approve user
@router.put("/users/{user_id}/approve")
def approve(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return approve_user(db, user_id)


@router.get("/users/petugas")
def get_petugas(
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return get_approved_petugas(db)


# ❌ Delete user
@router.delete("/users/{user_id}")
def delete(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return delete_user(db, user_id)