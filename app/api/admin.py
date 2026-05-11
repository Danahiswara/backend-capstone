from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.admin_service import (
    get_pending_users,
    approve_user,
    delete_user,
    reject_user,
    get_approved_petugas,
    create_type,
    update_type,
    get_types,
    delete_type,
    get_archived_types,
    restore_type
)
from app.schemas.type import TypeCreate, TypeResponse, TypeUpdate
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


@router.post("/types", response_model=TypeResponse)
def create_obat(
    payload: TypeCreate,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return create_type(
        db=db,
        name=payload.name,
        komposisi=payload.komposisi,
        farmasi=payload.farmasi,
        distributor=payload.distributor,
        total_items=payload.total_items
    )


@router.get("/types")
def get_all_obat(
    search: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return get_types(
        db=db,
        search=search,
        skip=skip,
        limit=limit
    )


@router.put("/types/{type_id}", response_model=TypeResponse)
def update_obat(
    type_id: int,
    payload: TypeUpdate,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return update_type(
        db=db,
        type_id=type_id,
        name=payload.name,
        komposisi=payload.komposisi,
        farmasi=payload.farmasi,
        distributor=payload.distributor,
        total_items=payload.total_items
    )


@router.delete("/types/{type_id}")
def delete_obat(
    type_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return delete_type(db, type_id)


@router.get("/types/archive")
def archived_obat(
    search: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return get_archived_types(
        db=db,
        search=search,
        skip=skip,
        limit=limit
    )


@router.put("/types/{type_id}/restore")
def restore_obat(
    type_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return restore_type(db, type_id)